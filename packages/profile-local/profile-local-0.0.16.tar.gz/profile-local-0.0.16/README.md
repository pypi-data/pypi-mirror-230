# settings.json configuration
This repository includes a settings.json file that allows you to customize the testing behavior of the project. It contains the following configuration options:

"python.testing.unittestArgs":
Usage: Specifies the arguments to be passed when running unit tests using the unittest framework.
Values: ["-v", "-s", "./tests", "-p", "test_*.py"]
- The -v flag enables verbose output, providing more detailed information about the test results. 
- The -s flag sets the starting directory for test discovery to ./tests, assuming test files are located in a directory named "tests" within your project. 
- The -p flag defines the pattern for discovering test files, which is set to test_*.py. Any Python file in the tests directory that starts with test_ will be considered a test file.

"python.testing.pytestEnabled" is set to false and "python.testing.unittestEnabled" is set to true so that the project with use the unittest framework for running tests, not the pytest framework. 
