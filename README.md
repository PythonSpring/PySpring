# **PySpring** Framework

#### **PySpring** is a Python web framework inspired by Spring Boot. It combines FastAPI for the web layer, SQLModel for ORM, and Pydantic for data validation. PySpring provides a structured approach to building scalable web applications with `auto dependency injection`, `auto configuration management`  and a `web server` for hosting your application.

# Key Features
- Application Initialization: **PySpringApplication** class serves as the main entry point for the **PySpring** application. It initializes the application from a configuration file, scans the application source directory for Python files, and groups them into class files and model files

- **Model Import and Table Creation**: **PySpring** dynamically imports model modules and creates SQLModel tables based on the imported models. It supports SQLAlchemy for database operations.

- **Application Context Management**: **PySpring** manages the application context and dependency injection. It registers application entities such as components, controllers, bean collections, and properties. It also initializes the application context and injects dependencies.

- **REST Controllers**: **PySpring** supports RESTful API development using the RestController class. It allows you to define routes, handle HTTP requests, and register middlewares easily.

- **Component-based Architecture**: **PySpring** encourages a component-based architecture, where components are reusable and modular building blocks of the application. Components can have their own lifecycle and can be registered and managed by the application context.

- **Properties Management**: Properties classes provide a convenient way to manage application-specific configurations. **PySpring** supports loading properties from a properties file and injecting them into components.

- **Framework Modules**: **PySpring** allows the integration of additional framework modules to extend the functionality of the application. Modules can provide additional routes, middlewares, or any other custom functionality required by the application.

- **Builtin FastAPI Integration**: **PySpring** integrates with `FastAPI`, a modern, fast (high-performance), web framework for building APIs with Python. It leverages FastAPI's features for routing, request handling, and server configuration.

# Getting Started
To get started with **PySpring**, follow these steps:

### 1. Install the **PySpring** framework by running:

`pip3 install git+https://github.com/PythonSpring/pyspring-core.git`


### 2. Create a new Python project and navigate to its directory

-  Implement your application properties, components, controllers, using **PySpring** conventions inside declared source code folder (whcih can be modified the key `app_src_target_dir` inside app-config.json), this controls what folder will be scanned by the framework.

- Instantiate a `PySpringApplication` object in your main script, passing the path to your application configuration file.

- Optionally, define and enable any framework modules you want to use.

- Run the application by calling the `run()` method on the `PySpringApplication` object, as shown in the example code below:

```python
from py_spring import PySpringApplication

def main():
    app = PySpringApplication()
    app.run()

if __name__ == "__main__":
    main()
```
- For example project, please refer to this [github repo](https://github.com/NFUChen/PySpring-Example-Project).

# Contributing

Contributions to **PySpring** are welcome! If you find any issues or have suggestions for improvements, please submit a pull request or open an issue on GitHub.