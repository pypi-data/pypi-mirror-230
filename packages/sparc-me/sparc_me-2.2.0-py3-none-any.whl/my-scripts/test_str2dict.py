import json
import ast

if __name__ == '__main__':
    # test_string = "{'spotlight': 'TRUE'}"
    # test_string = "{'spotlight': True}"
    test_string = "{'spotlight': True}"
    # converted = json.loads(test_string)
    # converted = ast.literal_eval(test_string)
    # converted = eval(test_string.replace("TRUE", "True"))
    converted = eval(test_string)

    print(converted)
