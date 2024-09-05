import yaml
from dataclasses import dataclass

class TestFile:
    """An abstraction over a test file.
    Currently, only YAML files are supported.
    """

    def __init__(self, file_content: str, file_name: str) -> None:
        self.groups = []

        # Get the file extension to determine which format should be used.
        extension = file_name.split(".")[-1]
        if extension == "yaml":
            try:
                # Tests are organised in groups of separate YAML documents (separated by "---")
                docs = yaml.safe_load_all(file_content)
                for test_group in docs:
                    tests = []
                    title = test_group.get("title", "")
                    for test in test_group.get("tests", []):
                        # Add an empty params field if none was provided.
                        if test.get("params") == None:
                            test["params"] = {}
                        
                        tests.append(SingleTest(test))

                    self.groups.append({"title": title, "tests": tests})
            except yaml.YAMLError as e:
                raise Exception(f'Error parsing YAML: {e}')
        else:
            raise Exception(f'"{extension}" files are not supported as a test format.')


class SingleTest:
    def __init__(self, test_dict: dict):
        self.answer = test_dict.get("answer", "")
        self.params = test_dict.get("params", {})
        self.desc = test_dict.get("description", "")

        self.sub_tests = []
        if "sub_tests" in test_dict:
            for sub_test in test_dict["sub_tests"]:
                expected_result = sub_test.get("expected_result")
                if not expected_result:
                    raise Exception("No expected result given for test")

                self.sub_tests.append(SubTest(
                    sub_test.get("description", ""),
                    sub_test.get("response", ""),
                    expected_result.get("is_correct"),
                    expected_result,
                ))
        else:
            expected_result = test_dict.get("expected_result")
            if not expected_result:
                raise Exception("No expected result given for test")

            self.sub_tests.append(SubTest(
                "",
                test_dict.get("response", ""),
                expected_result.get("is_correct"),
                expected_result,
            ))

    def evaluate_all(self, func) -> list[dict]:
        return [func(test.response, self.answer, self.params) for test in self.sub_tests]
    
    def compare_all(self, eval_results: list[dict]) -> tuple[bool, str]:
        for i, eval_result in enumerate(eval_results):
            eval_correct = eval_result["is_correct"]
                
            if eval_correct != self.sub_tests[i].is_correct:
                return (
                    False,
                    (f"response \"{self.sub_tests[i].response}\" with answer "
                     f"\"{self.answer}\" was {'' if eval_correct else 'in'}correct: "
                     f"{eval_result['feedback']}\nTest description: {self.sub_tests[i].desc}")
                )
            
            # Are there any other fields in the eval function result that need to be checked?
            if self.sub_tests[i].expected_result != None:
                # Check each one in turn
                for key, value in self.sub_tests[i].expected_result.items():
                    actual_result_val = eval_result.get(key)
                    if actual_result_val == None:
                        return (False, f"No value returned for \"{key}\"")
                    
                    if actual_result_val != value:
                        return (
                            False,
                            f"expected {key} = \"{value}\", got {key} = \"{actual_result_val}\"\nTest description: {self.desc}"
                        )
        
        return (True, "")

@dataclass
class SubTest:
    desc: str
    response: str
    is_correct: bool
    expected_result: dict


def auto_test(path, func):
    """A decorator that adds the necessary infrastructure to run tests defined
    in an external data file.\n
    `path`: the path to the data file, relative to the eval function root.\n
    `func`: the function to test. Should usually be `evaluation_function`.
    """
    def _auto_test(orig_class):
        def test_auto(self):
            # Creating a TestFile can fail for several reasons.
            # If so, an exception is raised with a suitable error message
            tests = {}
            try:
                with open(path, "r") as f:
                    tests = TestFile(f.read(), path)
            except Exception as e:
                self.fail(e)

            # Successfully loaded 
            for group in tests.groups:
                for test in group["tests"]:
                    results = test.evaluate_all(func)
                    self.assertTrue(*test.compare_all(map(lambda r: r.to_dict(), results)))

        orig_class.test_auto = test_auto # Add the test_auto function to the class
        return orig_class
    return _auto_test
