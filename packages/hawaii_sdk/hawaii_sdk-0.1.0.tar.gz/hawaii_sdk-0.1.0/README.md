[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/hawaii-sdk/badge/?version=latest)](https://hawaii-sdk.readthedocs.io/en/latest/?badge=latest)
[![Test and Build](https://github.com/ThatsTheEnd/sdk_development/actions/workflows/python-app.yml/badge.svg)](https://github.com/ThatsTheEnd/sdk_development/actions/workflows/python-app.yml)



# Hawaii `sdk_development` - A Streamlined SDK for our Devices over Websocket Communication

Welcome to `sdk_development`! 

Here, we're building a versatile SDK for our devices. It's designed to be efficient, readable, and a touch of fun.

## Features

- **Communication**: Our foundational layer to manage all kinds of interactions.
- **WebSocketClient**: A WebSocket-based communication module.
- **Message Parsing**: Tools for message structuring and error handling.
- **Devices**: Interfaces and implementations for various devices like CCD Cameras and Monochromators.

## Getting Started

### Prerequesits
These code pieces rely on an installed version of the SDK.

1. Log into [hawaii.com](www.hawaii.com) with your user account or create a new account
2. Enter your hawaii hardware serial number(s) to see if you have access to the SDK
3. Download and install the SDK
4. You can a successful installation by running the following commands in a shell:

   ```sh
   MySDK --version
   ```
   This must return a version string, e.g. "1.7.3"

5. Run one of the *hello world* examples in the [examples](./examples/) section of this repo.

### As a SDK user
Code examples for different programming languages like _Python_, _LabVIEW_ and _C#_ can be found in the [examples](./examples/)
Instruction videos on how to use the SDK can be found on the [hawaii youtube channel](https://www.youtube.com/user/hawaiiScientificVDO)
The full documentation of the APi can be found on [Read the docs](https://readthedocs.org/)

### As Contributor to the SDK
This package is built with poetry, so make sure to head over to [Poetry](https://python-poetry.org/docs/basic-usage/) to get started.

1. **Installation**:
    ```bash
   cd /PathWhereYouWantThisRepo 
   git clone https://github.com/ThatsTheEnd/sdk_development.git .
   cd sdk_development
   pip install poetry
   poetry install
    ```

2. **Running Tests**:
    ```bash
    poetry run pytest
    ```

3. **Documentation**:
   Navigate to the `docs` directory for in-depth information.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Structure

- **`sdk_development`**: Core source code.
- **`tests`**: Unit tests to ensure everything runs smoothly.
- **`scripts`**: Utility scripts.
- **`docs`**: Comprehensive documentation.

## Contributing

1. **Bug Reports & Feature Requests**: Use GitHub issues to report any bugs or suggest features.
2. **Pull Requests**: Always welcome! Ensure tests pass before submitting.

## License

MIT. See the `LICENSE` file for details.
