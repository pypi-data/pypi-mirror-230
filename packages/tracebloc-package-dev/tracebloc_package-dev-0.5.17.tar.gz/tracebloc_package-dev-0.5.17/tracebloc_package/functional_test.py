import sys
from silence_tensorflow import silence_tensorflow

silence_tensorflow()
import os
import dis
import re
import shutil
from torch.utils.data import DataLoader
from collections import OrderedDict
import torch.optim as optim
import torch.nn as nn
import torchvision.datasets as datasets
from inspect import getmembers, isfunction
from .utils import *


# base class for checks on model file
class CheckModel:
    MAX_MODEL_NAME_LENGTH = 64
    message = ""
    model = None
    tmp_file_path = ""
    file_name = "model.py"
    tmp_file = ""
    main_method = ""
    main_class = ""
    input_shape = ""
    output_classes = ""
    image_size = 224
    batch_size = 16
    framework = ""
    notallowed = ["__MACOSX", "__pycache__"]
    input_shape_patt = re.compile("(^input_shape\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    out_classes_patt = re.compile("(^output_classes\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_method_patt = re.compile("(^main_method\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    main_class_patt = re.compile("(^main_class\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    framework_patt = re.compile("(^framework\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    image_size_patt = re.compile("(^image_size\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")
    batch_size_patt = re.compile("(^batch_size\s{0,}[=]\s{0,}[a-zA-Z_\-0-9'\"])")

    def __init__(
        self, progress_bar, model_name=None, model_path=None
    ):  # pragma: no cover
        self.model_name = model_name
        self.model_path = model_path
        self.progress_bar = progress_bar
        self.file_not_allowed = False

    def prepare_file(self, temp_file):
        try:
            main_file, remove_lines, filelines = self.get_variables(temp_file)
            if main_file and self.framework == TENSORFLOW_FRAMEWORK:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                if self.main_method == "":
                    self.load_model(temp_file)
                    self.add_method(temp_file, remove_lines)
                else:
                    self.edit_file(temp_file, filelines, remove_lines)
            elif self.framework == PYTORCH_FRAMEWORK and main_file:
                self.tmp_file = os.path.join(self.tmp_file_path, self.file_name)
                self.edit_file(temp_file, filelines, remove_lines)
            elif main_file and self.framework == "":
                raise Exception("\nFramework argument missing in file")
        except Exception as e:
            raise e

    def get_variables(self, temp_file):
        main_file = False
        remove_lines = []
        with open(temp_file, "r") as tmp_fp:
            filedata = tmp_fp.read()
            if TORCH_HUB_PATTERN in filedata:
                self.file_not_allowed = True
        filelines = filedata.split("\n")
        tensorflow_pattern_dict = {
            self.input_shape_patt: "input_shape",
            self.out_classes_patt: "output_classes",
            self.main_method_patt: "main_method",
        }
        pytorch_pattern_dict = {
            self.main_class_patt: "main_class",
            self.image_size_patt: "image_size",
            self.batch_size_patt: "batch_size",
        }
        for linenum, fileline in enumerate(filelines):
            if self.framework_patt.match(fileline):
                self.framework = re.sub(
                    "(framework\s{0,}[=]\s{0,})",
                    "",
                    fileline.replace("'", "").replace('"', ""),
                )
                remove_lines.append(linenum)
                if not main_file:
                    self.file_name = os.path.split(temp_file)[1]
                    main_file = True
            if self.framework == TENSORFLOW_FRAMEWORK:
                for pattern, attribute in tensorflow_pattern_dict.items():
                    if pattern.match(fileline):
                        setattr(
                            self,
                            attribute,
                            re.sub(
                                f"({attribute}\s{{0,}}[=]\s{{0,}})",
                                "",
                                fileline.replace("'", "").replace('"', ""),
                            ),
                        )
                        remove_lines.append(linenum)
                        if not main_file:
                            self.file_name = os.path.split(temp_file)[1]
                            main_file = True
                        break
            elif self.framework == PYTORCH_FRAMEWORK:
                for pattern, attribute in pytorch_pattern_dict.items():
                    if pattern.match(fileline):
                        setattr(
                            self,
                            attribute,
                            re.sub(
                                f"({attribute}\s{{0,}}[=]\s{{0,}})",
                                "",
                                fileline.replace("'", "").replace('"', ""),
                            ),
                        )
                        remove_lines.append(linenum)
                        if not main_file:
                            self.file_name = os.path.split(temp_file)[1]
                            main_file = True
                        break
        if main_file and self.framework == "":
            print("Framework parameter missing from file")
            return False, [], []
        tmp_fp.close()
        return main_file, remove_lines, filelines

    def replace_vars(self, code):
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.input_shape}[^a-zA-Z_\-0-9]", code):
            allresultsi = re.findall(
                f"[^a-zA-Z_\-0-9]{self.input_shape}[^a-zA-Z_\-0-9]", code
            )
            if allresultsi == []:
                allresultsi = re.findall(f"{self.input_shape}[^a-zA-Z_\-0-9]", code)
            for found in allresultsi:
                replace_text = found.replace(self.input_shape, "input_shape")
                code = code.replace(found, replace_text)
        if re.search(
            f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
        ) or re.search(f"{self.output_classes}[^a-zA-Z_\-0-9]", code):
            allresultso = re.findall(
                f"[^a-zA-Z_\-0-9]{self.output_classes}[^a-zA-Z_\-0-9]", code
            )
            if allresultso == []:
                allresultso = re.findall(f"{self.output_classes}[^a-zA-Z_\-0-9]", code)
            for found in allresultso:
                replace_text = found.replace(self.output_classes, "output_classes")
                code = code.replace(found, replace_text)
        return code

    def edit_file(self, temp_file, filelines, remove_lines=[]):
        edited_data = []
        with open(temp_file, "w") as tmp_fp:
            for linenum, fileline in enumerate(filelines):
                if linenum in remove_lines:
                    continue
                else:
                    if self.framework == TENSORFLOW_FRAMEWORK:
                        if re.search(f"def {self.main_method}\(.*\)", fileline):
                            fileline = fileline.replace(
                                str(self.main_method), "MyModel"
                            )
                        fileline = self.replace_vars(fileline)
                    elif self.framework == PYTORCH_FRAMEWORK:
                        if re.search(f"class {self.main_class}\(.*\)", fileline):
                            fileline = fileline.replace(str(self.main_class), "MyModel")
                    edited_data.append(fileline)
            tmp_fp.writelines("\n".join(edited_data))
        tmp_fp.close()

    def get_imports(self, codelines):
        instructions = dis.get_instructions(codelines)
        instructions = [__ for __ in instructions]
        line = 0
        import_line_num = []
        for inst in instructions:
            if inst.starts_line is not None:
                line = inst.starts_line
            if "IMPORT" in inst.opname:
                if line not in import_line_num:
                    import_line_num.append(line)
        return import_line_num

    def get_parameters(self, codelines, remove_lines=[]):
        import_lines = []
        myMethod = []
        input_shape = ""
        output_classes = ""
        return_obj = ""
        all_members = getmembers(self.model)
        for member_name, member_type in all_members:
            if isinstance(member_type, tf.keras.Sequential):
                return_obj = member_name

        import_line_nums = self.get_imports(codelines)
        codelines = codelines.split("\n")
        for linenum, code in enumerate(codelines):
            if (
                re.search("(.*\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", code)
                and return_obj == ""
            ):
                return_obj = re.sub(
                    "(\s{0,}=\s{0,}[tf.]{0,}[keras.]{0,}Model\(.*\))", "", code
                )
            code = self.replace_vars(code)
            if code == "":
                continue
            elif (linenum) in remove_lines:
                continue
            elif (linenum + 1) in import_line_nums:
                import_lines.append(code.strip())
            elif re.search("(input_shape\s{0,}[=]\s{0,}\([0-9\, ]{7,}\))", code):
                input_shape = re.sub("(input_shape\s{0,}[=]\s{0,})", "", code)
            elif re.search("(output_classes\s{0,}[=]\s{0,})", code):
                output_classes = re.sub("(output_classes\s{0,}[=]\s{0,})", "", code)
            else:
                code = code.replace("    ", "\t")
                myMethod.append(code)
        return import_lines, input_shape, output_classes, myMethod, return_obj

    def prepare_wrapper_code(self, codelines, remove_lines=[]):
        codeparts = self.get_parameters(codelines, remove_lines)
        updated_code = "\n".join(codeparts[0])
        updated_code = "\n".join(
            [
                updated_code,
                f"\ndef MyModel(input_shape={codeparts[1]}, output_classes={codeparts[2]}):",
            ]
        )
        updated_code = "\n\t".join([updated_code, "\n\t".join(codeparts[3])])
        updated_code = "\n\t".join([updated_code, f"return {codeparts[4]}"])
        return updated_code

    def add_method(self, file="", remove_lines=[]):
        try:
            if file == "":
                file = self.tmp_file
            file_obj = open(f"{file}", "r")
            codelines = file_obj.read()
            updated_code = self.prepare_wrapper_code(codelines, remove_lines)
            file_obj.close()
            file_obj = open(f"{file}", "w")
            file_obj.write(updated_code)
            file_obj.close()
        except:
            self.message = "Model file not provided as per docs"
            raise

    def check_MyModel(self):
        """
        Check if model is MyModel is present in model file
        """
        try:
            getmembers(self.model.MyModel, isfunction)
            self.progress_bar.update(1)
        except Exception:  # pragma: no cover
            self.message = "Please upload file as per docs"
            raise

    def load_model(self, filename="", update_progress_bar=False):
        if filename == "":
            filename = self.file_name
        try:
            sys.path.append(self.tmp_file_path)
            self.model = SourceFileLoader(
                f"{filename}", f"{self.tmp_file}"
            ).load_module()
            if self.framework == PYTORCH_FRAMEWORK:
                self.model = self.model.MyModel()
            if update_progress_bar:
                self.progress_bar.update(1)
        except Exception as e:
            if self.message == "":
                self.message = f"Error loading the model file, {str(e)}"
            raise

    def extract_multiple_file(self):
        import zipfile

        with open(self.model_path, "rb") as file:
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(self.tmp_file_path)
        return False

    def load_model_file(self):
        self.tmp_file_path = os.path.join(
            self.model_path.rsplit("/", 1)[0],
            f"tmpmodel_{self.model_name[: self.MAX_MODEL_NAME_LENGTH]}",
        )
        if not os.path.isdir(self.tmp_file_path):
            os.mkdir(self.tmp_file_path)
        # check if file contains the MyModel function
        try:
            file = self.model_path.rsplit("/", 1)[1]
            if os.path.splitext(str(file))[1] == ".zip":
                self.extract_multiple_file()
            else:
                self.tmp_file = os.path.join(self.tmp_file_path, str(file))
                self.file_name = str(file)
                shutil.copy2(self.model_path, self.tmp_file_path)
            for tmp_f in os.listdir(self.tmp_file_path):
                if not (os.path.isdir(tmp_f) or tmp_f in self.notallowed):
                    self.prepare_file(os.path.join(self.tmp_file_path, tmp_f))
            self.load_model(filename=self.file_name)
            if self.framework == TENSORFLOW_FRAMEWORK:
                self.check_MyModel()
                self.check_model_arguments()
            else:
                self.progress_bar.update(2)
        except Exception as e:  # pragma: no cover
            if os.path.exists(self.tmp_file_path):
                shutil.rmtree(self.tmp_file_path)
            if self.message == "":
                self.message = f"\nError loading the model file as {e}"
            raise

    def check_model_arguments(self):
        """
        Check if MyModel contains:
            - input_shape
            - classes
        """
        try:
            self.model = self.model.MyModel(input_shape=(256, 256, 3), output_classes=1)
            self.progress_bar.update(1)
        except Exception:  # pragma: no cover
            self.message = "\nModel file not provided as per docs: MyModel function receives no arguments"
            raise

    def remove_tmp_file(self, update_progress_bar=False):
        """
        remove temporary model file
        """
        if os.path.exists(self.tmp_file_path):  # pragma: no cover
            shutil.rmtree(self.tmp_file_path)
        if update_progress_bar:
            self.progress_bar.update(1)

    def model_func_checks(self):
        # check if model is eligible
        try:
            self.load_model_file()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            self.message = f"\n\nModel checks failed with error as {e}"
            eligible = False
        if self.file_not_allowed:
            self.message = f"\n\nWe dont support torch hub models, please provide torchvision models"
            eligible = False
        if not eligible:
            return eligible, self.message, None, self.progress_bar  # pragma: no cover
        return True, self.message, self.model_name, self.progress_bar


class TensorflowChecks:
    def __init__(self, **kwargs):
        validate_kwargs(
            kwargs,
            {
                "model",
                "model_name",
                "message",
                "progress_bar",
                "image_size",
                "batch_size",
                "tmp_path",
            },
        )
        self.message = kwargs["message"]
        self.model = kwargs["model"]
        self.model_name = kwargs["model_name"]
        self.progress_bar = kwargs["progress_bar"]
        self.image_size = kwargs["image_size"]
        self.batch_size = kwargs["batch_size"]
        self.tmp_path = kwargs["tmp_path"]
        self.average_weights_file_path = None

    def progress_bar_update(self):
        if self.progress_bar is not None:
            self.progress_bar.update(1)

    def is_model_supported(self):
        """
        Check if model contains:
            - input_shape
            - classes
        """
        tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
        model = self.model
        supported = isinstance(model, tensorflow_supported_apis)
        if supported:  # pragma: no cover
            # check if it is of model subclassing api
            if not hasattr(model, "input_shape"):
                self.message = "\nModel file not provided as per docs: unsupported API used for Model"  # pragma: no cover
                raise Exception("input shape missing")  # pragma: no cover
        self.progress_bar_update()

    def layer_instance_check(self):
        """
        If model layers are of type keras layers
        """
        for layer in self.model.layers:
            if not isinstance(layer, tf.keras.layers.Layer):
                self.message = "\nLayers in Model are not supported by Tensorflow"  # pragma: no cover
                raise Exception("invalid layer")  # pragma: no cover
        self.progress_bar_update()

    def small_training_loop(self, weight_filename, custom_loss=None):
        try:
            # mock dataset for small training
            classes = 1  # get output classes from model
            training_dataset = mock_dataset(classes)
            if custom_loss:
                # check for custom loss
                loss = custom_loss["value"]
            else:
                loss = tf.keras.losses.BinaryCrossentropy()
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(),
                loss=loss,
            )
            self.model.fit(training_dataset, epochs=1, verbose=0)
            if weight_filename == PRETRAINED_WEIGHTS_FILENAME:
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=TENSORFLOW_FRAMEWORK,
                )
            else:
                # dump weights from trained model will be used in averaging check
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=TRAINED_WEIGHTS_FILENAME,
                    framework=TENSORFLOW_FRAMEWORK,
                )
                self.progress_bar_update()
        except Exception as e:  # pragma: no cover
            self.message = (
                "\nModel not support training on image classification dataset."
            )
            raise

    def check_original_model_channels(self):
        """
        check for model channels to be 3
        """
        model_channel = self.model
        if model_channel.input_shape[3] != 3:
            self.message = (
                "\nPlease provide model input shape with 3 channels"  # pragma: no cover
            )
            raise Exception("invalid input shape")  # pragma: no cover
        self.progress_bar_update()

    def resize_weight_arrays(self, weights_list_tuple):
        # Find the maximum shape among all weight arrays in the tuple
        max_shape = np.array(max(w.shape for w in weights_list_tuple))

        # Broadcast each weight array to the maximum shape
        resized_weights_list = []
        for w in weights_list_tuple:
            if w.shape == ():
                # Convert 0-dimensional array to 1-dimensional array
                broadcasted_w = np.broadcast_to(w, (1,))
            else:
                broadcasted_w = np.broadcast_to(w, max_shape)
            resized_weights_list.append(broadcasted_w)

        return resized_weights_list

    def average_weights(self):
        weights = []
        new_weights = []
        no_images_array = [20, 20]
        weights_file_path_1 = os.path.join(
            self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pkl"
        )
        weights_file_path_2 = os.path.join(
            self.tmp_path, f"{TRAINED_WEIGHTS_FILENAME}.pkl"
        )
        self.average_weights_file_path = os.path.join(
            self.tmp_path, f"{AVERAGED_WEIGHTS_PATH}.pkl"
        )
        try:
            with open(weights_file_path_1, "rb") as pkl_file, open(
                weights_file_path_2, "rb"
            ) as pkl_file2:
                weights.append(pickle.load(pkl_file))
                weights.append(pickle.load(pkl_file2))
        except Exception as e:
            raise
        try:
            new_weights = [
                np.array(
                    [
                        np.average(np.array(w), weights=no_images_array, axis=0)
                        for w in zip(*self.resize_weight_arrays(weights_list_tuple))
                    ]
                )
                for weights_list_tuple in zip(*weights)
            ]
            del weights
            del no_images_array
        except Exception as e:
            raise
        try:
            with open(self.average_weights_file_path, "wb") as f:
                pickle.dump(new_weights, f)
            del new_weights
        except Exception as e:
            raise

    def load_averaged_weights(self):
        try:
            with open(self.average_weights_file_path, "rb") as f:
                parameters = pickle.load(f)
            self.model.set_weights(parameters)
            del parameters
        except Exception as e:
            raise

    def is_model_eligible(self):
        try:
            self.is_model_supported()
            self.check_original_model_channels()
            self.layer_instance_check()
            if not os.path.exists(
                os.path.join(self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pkl")
            ):
                self.small_training_loop(PRETRAINED_WEIGHTS_FILENAME)
            self.small_training_loop(TRAINED_WEIGHTS_FILENAME)
            self.average_weights()
            self.load_averaged_weights()
            self.message = "\nall check passed"
        except Exception as e:  # pragma: no cover
            self.message = f"\n\nModel checks failed with error as {e}"
            return False, self.message
        return True, self.message

    def model_func_checks(self):
        # check if model is eligible
        eligible, message = self.is_model_eligible()
        if not eligible:
            return eligible, message, None, self.progress_bar  # pragma: no cover
        return True, self.message, self.model_name, self.progress_bar


class TorchChecks:
    def __init__(self, **kwargs):
        validate_kwargs(
            kwargs,
            {
                "model",
                "model_name",
                "message",
                "progress_bar",
                "image_size",
                "batch_size",
                "tmp_path",
            },
        )
        self.message = kwargs["message"]
        self.model = kwargs["model"]
        self.model_name = kwargs["model_name"]
        self.progress_bar = kwargs["progress_bar"]
        self.image_size = kwargs["image_size"]
        self.batch_size = kwargs["batch_size"]
        self.tmp_path = kwargs["tmp_path"]
        self.average_weights_file_path = None

    def is_model_supported(self):
        """
        Check if model contains:
            - forward function
        """
        model = self.model
        if not hasattr(model, "forward"):
            self.message = "\nModel file not provided as per docs: forward function not found in  Model"
            raise Exception("forward func missing")
        self.progress_bar.update(1)

    def small_training_loop(self, weight_filename, custom_loss=None):
        try:
            # Define the number of fake images and other properties
            num_images = 100
            num_channels = 3
            num_classes = 2
            # Create fake image data
            train_dataset = datasets.FakeData(
                size=num_images,
                image_size=(num_channels, self.image_size, self.image_size),
                num_classes=num_classes,
                transform=transforms.ToTensor(),
            )

            train_loader = DataLoader(
                train_dataset, batch_size=self.batch_size, shuffle=True
            )

            # train_loader, classes = mock_torch_data(self.tmp_path)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)
            for epoch in range(1):  # loop over the dataset multiple times
                running_loss = 0.0
                for i, data in enumerate(train_loader, 0):
                    # get the inputs; data is a list of [inputs, labels]
                    inputs, labels = data
                    labels = torch.tensor(labels, dtype=torch.long)
                    # zero the parameter gradients
                    optimizer.zero_grad()

                    # forward + backward + optimize
                    outputs = self.model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    # print statistics
                    running_loss += loss.item()
            # dump weights from trained model will be used in averaging check
            if weight_filename == PRETRAINED_WEIGHTS_FILENAME:
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                )
            else:
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=TRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                )
                self.progress_bar.update(1)
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel not support training on image classification dataset as there is error {e} "
            raise

    def resize_weight_arrays(self, weights_list_tuple):
        # Find the maximum shape among all weight arrays in the tuple
        max_shape = np.array(max(w.shape for w in weights_list_tuple))

        # Broadcast each weight array to the maximum shape
        resized_weights_list = []
        for w in weights_list_tuple:
            if w.shape == ():
                # Convert 0-dimensional array to 1-dimensional array
                broadcasted_w = np.broadcast_to(w, (1,))
            else:
                broadcasted_w = np.broadcast_to(w, max_shape)
            resized_weights_list.append(broadcasted_w)

        return resized_weights_list

    def average_weights(self):
        weights = []
        new_weights = []
        no_images_array = [100, 100]
        weights_file_path_1 = os.path.join(
            self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pkl"
        )
        weights_file_path_2 = os.path.join(
            self.tmp_path, f"{TRAINED_WEIGHTS_FILENAME}.pkl"
        )
        self.average_weights_file_path = os.path.join(
            self.tmp_path, f"{AVERAGED_WEIGHTS_PATH}.pkl"
        )
        try:
            with open(weights_file_path_1, "rb") as pkl_file, open(
                weights_file_path_2, "rb"
            ) as pkl_file2:
                weights.append(pickle.load(pkl_file))
                weights.append(pickle.load(pkl_file2))
        except Exception as e:
            raise
        try:
            new_weights = [
                np.array(
                    [
                        np.average(np.array(w), weights=no_images_array, axis=0)
                        for w in zip(*self.resize_weight_arrays(weights_list_tuple))
                    ]
                )
                for weights_list_tuple in zip(*weights)
            ]
            del weights
            del no_images_array
        except Exception as e:
            raise
        try:
            with open(self.average_weights_file_path, "wb") as f:
                pickle.dump(new_weights, f)
            del new_weights
        except Exception as e:
            raise e

    def load_averaged_weights(self):
        try:
            with open(self.average_weights_file_path, "rb") as f:
                parameters = pickle.load(f)
            params_dict = zip(self.model.state_dict().keys(), parameters)
            state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
            self.model.load_state_dict(state_dict, strict=True)
            self.progress_bar.update(1)
            del params_dict
            del state_dict
            del parameters
        except Exception as e:
            raise

    def model_func_checks(self):
        # check if model is eligible
        try:
            self.is_model_supported()
            if os.path.exists(
                os.path.join(self.tmp_path, f"{PRETRAINED_WEIGHTS_FILENAME}.pth")
            ):
                get_model_parameters(
                    model=self.model,
                    weight_file_path=self.tmp_path,
                    weights_file_name=PRETRAINED_WEIGHTS_FILENAME,
                    framework=PYTORCH_FRAMEWORK,
                )
                self.progress_bar.update(1)
            else:
                self.small_training_loop(PRETRAINED_WEIGHTS_FILENAME)
                self.progress_bar.update(1)
            self.small_training_loop(TRAINED_WEIGHTS_FILENAME)
            self.average_weights()
            self.load_averaged_weights()
            self.message = "all check passed"
            eligible = True
        except Exception as e:  # pragma: no cover
            self.message = f"\nModel checks failed with error as {e}"
            eligible = False
        if not eligible:
            return eligible, self.message, None, self.progress_bar  # pragma: no cover
        return eligible, self.message, self.model_name, self.progress_bar
