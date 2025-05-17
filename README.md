# 📰 Hacker News Scraper API

Welcome to the **Hacker News Scraper API**! This API allows you to fetch news articles from the Hacker News website in a structured and efficient way. 🚀

## Table of Contents

- [📋 Requirements](#requirements)
- [📁 Project Structure](#project-structure)
- [📦 Dependency Management with Poetry](#dependency-management-with-poetry)
- [🔧 Project setup](#project-setup)
- [📜 API Documentation](#api-documentation)
- [🧹 Code Quality](#code-quality)
- [🧪 Unit tests](#unit-tests)
- [🚀 Continuous Integration](#continuous-integration)


## 📋 Requirements

Before you begin, ensure you have the following prerequisites installed on your machine:

- [Python 3.10](https://www.python.org/downloads/) or higher
- [Poetry](https://python-poetry.org/docs/#installation)


## 📁 Project Structure

The project is organized following this structure:

```
├── app
│   ├── api
│   │   └── routes
│   ├── dependencies
│   │   └── redis.py
│   └── main.py
├── docker
│   └── Dockerfile
├── docker-compose.yaml
├── poetry.lock
├── pyproject.toml
└── tests
    └── test_hacker_news.py
```

This project uses [Poetry](https://python-poetry.org/) for dependency management. Poetry simplifies the process of managing dependencies and packaging Python projects.

Once installed, you can easily manage dependencies by running `poetry add <dependency>` to add the new dependency and running `poetry install --no-root`, to install all the required packages listed in the [`pyproject.toml`](pyproject.toml) file.


## 🔧 Project Setup

To deploy the **Hacker News Scraper API**, follow these steps:

1. **Start the API using Docker Compose**
    Run the following command to build and start the services:

    ```bash
    docker compose up --build
    ```

    Once the services are up, the API will be available at [http://localhost:3000](http://localhost:3000).

2. **Access Redis Information**
    You can also access Redis content or monitor its status at [http://localhost:8001](http://localhost:8001).

3. **Test the API**
    Use the following `curl` command to test the API and view the results in a structured format:

    ```bash
    curl -s localhost:3000 | jq
    ```

    Example output:

    ```json
    [
      {
         "title": "Coding Without a Laptop – Two Weeks with AR Glasses and Linux on Android",
         "url": "https://holdtherobot.com/blog/2025/05/11/linux-on-android-with-ar-glasses/",
         "sent_by": "mikenew",
         "published": "4 hours ago"
      },
      {
         "title": "Large Language Models Are More Persuasive Than Incentivized Human Persuaders",
         "url": "https://arxiv.org/abs/2505.09662",
         "sent_by": "flornt",
         "published": "1 hour ago"
      }
      ...
    ]
    ```

## 📂 Custom Shared Library Integration

This project utilizes a custom shared library containing generic and reusable implementations for services like logging and Redis integration. These implementations are designed to be modular and can be utilized across different projects, promoting code reusability and maintainability.

The shared library is integrated into this project using Poetry, ensuring seamless compatibility with the existing codebase. By leveraging this shared library, the project benefits from pre-built solutions for common services, reducing development time and improving consistency across projects.

The shared library can be accessed at [https://github.com/renatoramossilva/bindl-lib](https://github.com/renatoramossilva/bindl-lib).


## 📜 API Documentation

You can find the API documentation at the following link: [API Documentation](http://localhost:3000/docs)


## 🧹 Code Quality

This project uses several tools to maintain code quality and enforce coding standards:

- **[black](https://black.readthedocs.io/)**: A code formatter that ensures consistent code style.
- **[ruff](https://docs.astral.sh/ruff/)**: Python linter and code formatter
- **[mypy](http://mypy-lang.org/)**: A static type checker to ensure type safety in Python code.

These tools are integrated with [pre-commit](https://pre-commit.com/), ensuring that they are automatically run before each commit to maintain code quality.

To manually run these tools, you can use this command:

`poetry run pre-commit run --all-files`


## 🧪 Unit tests

This project uses `pytest` for unit testing to ensure the functionality of key features like car bookings and availability checks.

### Running Tests

To run the unit tests locally:

`poetry run pytest`


## 🚀 Continuous Integration

Whenever a pull request is opened, the [GitHub Actions workflow](https://github.com/renatoramossilva/ta-flnks-pe/actions) will trigger and perform the following checks:

- Code Formatting: Run `black` and `ruff` to format the code.
- Static Analysis: Execute `mypy` to ensure code quality.
- Unit Testing: Run `pytest` to execute the unit tests

This setup ensures that only code that passes all checks is merged into the master branch, maintaining a high standard of code quality throughout the development process.

Happy Scraping! 🎉
