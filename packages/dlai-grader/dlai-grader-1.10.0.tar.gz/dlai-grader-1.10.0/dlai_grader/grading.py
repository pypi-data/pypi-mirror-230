from dataclasses import dataclass
from functools import wraps
from types import ModuleType
from typing import Any, Callable, List, Tuple


@dataclass
class LearnerSubmission:
    """Class that represents a file from the learner. Useful when grading does not depend on the notebook"""

    submission: Any = None


@dataclass
class test_case:
    """Class that represents a test case"""

    msg: str = ""
    want: Any = None
    got: Any = None
    failed: bool = False


@dataclass
class aggregated_test_case:
    """Class that represents an aggregated collection of test cases"""

    test_name: str
    tests: List[test_case]


def compute_grading_score(
    test_cases: List[test_case],
) -> Tuple[float, str]:
    """Computes the score based on the number of failed and total cases.
    Args:
        test_cases (List): Test cases.
    Returns:
        Tuple[float, str]: The grade and feedback message.
    """

    num_cases = len(test_cases)
    failed_cases = [t for t in test_cases if t.failed == True]
    score = 1.0 - len(failed_cases) / num_cases
    feedback_msg = "All tests passed! Congratulations!"

    if failed_cases:
        feedback_msg = ""
        for failed_case in failed_cases:
            feedback_msg += f"Failed test case: {failed_case.msg}.\nExpected:\n{failed_case.want},\nbut got:\n{failed_case.got}.\n\n"
        return round(score, 2), feedback_msg

    return score, feedback_msg


def compute_aggregated_grading_score(
    aggregated_test_cases: List[aggregated_test_case],
) -> Tuple[float, str]:
    """Computes the score based on the number of failed and total cases.
    Args:
        aggregated_test_cases (List): Aggregated test cases for every part.
    Returns:
        Tuple[float, str]: The grade and feedback message.
    """
    scores = []
    msgs = []

    for test_cases in aggregated_test_cases:
        feedback_msg = f"All tests passed for {test_cases.test_name}!\n"
        num_cases = len(test_cases.tests)
        failed_cases = [t for t in test_cases.tests if t.failed == True]
        score = 1.0 - len(failed_cases) / num_cases
        score = round(score, 2)
        scores.append(score)

        if failed_cases:
            feedback_msg = f"Details of failed tests for {test_cases.test_name}\n\n"
            for failed_case in failed_cases:
                feedback_msg += f"Failed test case: {failed_case.msg}.\nExpected:\n{failed_case.want},\nbut got:\n{failed_case.got}.\n\n"
        msgs.append(feedback_msg)

    final_score = sum(scores) / len(scores)
    final_score = round(final_score, 2)
    final_msg = "\n".join(msgs)

    return final_score, final_msg


def object_to_grade(
    origin_module: ModuleType,
    *attr_names: str,
) -> Callable[[Callable[[Any], List[test_case]]], Callable[[Any], List[test_case]]]:
    """Used as a parameterized decorator to get any number of attributes from a module.
    Args:
        origin_module (ModuleType): A module.
        attrs_name (Tuple[str, ...]): Names of the attributes to extract from the module.
    """

    def middle(func):
        @wraps(func)
        def wrapper():
            original_attrs = []
            for atrr in attr_names:
                original_attr = getattr(origin_module, atrr, None)
                original_attrs.append(original_attr)

            return func(*original_attrs)

        return wrapper

    return middle
