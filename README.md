# user-management

`user-management` is a User Management template for creating a FastApi server utilizing MongoDB. 

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.12.4

### Installing

Follow these steps to get your development environment running:

1. **Clone the repository**

   ```sh
   git clone https://github.com/zaalgol/user-management.git

2. **Navigate to the project director**

   ```sh
   cd user-management
   ```

3. **Copy the content of .env_template to a new .env file**


4. **Edit the .env file**

   edit and add missing values.
   note: Need to edit CA_FILE value only if you are using a external MongoDB

5. **Create a veirtual Environment (Optional)**

6. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

7. **move to development mode (to resolve pathes issue)**
   ```sh
   pip install -e .
   ```

## Running the Tests

   ```sh
   pytest tests
   ```

## Contributing

If you have suggestions for improving the project, please fork the repo and submit a pull request. You can also open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

## Versioning

For the versions available, see the [tags on this repository](https://github.com/zaalgol/user-management/tags).

## Authors

- **Zalman Goldstein** - *Initial work* - [ZaalGol](https://github.com/zaalgol)

See also the list of [contributors](https://github.com/zaalgol/user-management/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hat tip to anyone whose code was used as inspiration.
- Thanks to the FastApi, MongoDB, and other communities for their invaluable resources.
