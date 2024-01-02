# Driver Drowsiness Detection

This is a deep learning-powered application that detects whether the driver who is driving the vehicle is sleeping or not sleeping.

## How to Run?

### STEPS:

1. Clone the repository
   ```bash
    git clone  https://github.com/surajkarki66/driver_drowsiness_detection
    ```

2. Create a Python virtual environment and activate the environment based on your machine(Linux, MacOS, and Windows)

3. Install the dependencies
   ```bash
    make install
   ```
4. Create a `.env` file in a project root directory and set all the environment variables based on the provided `.env.sample` example.

5. Migrate the database
   ```bash
    make migrate
    ```


6. If you want to create a super user then enter the following command.
    ```bash
    make superuser
    ```

7. Run the development server
    ```bash
    make run-server
    ```

Now, open the web browser and go to the given address: `http://127.0.0.1:8000/`

To access the admin panel click here: `http://127.0.0.1:8000/admin`


Note: There are also lots of REST APIs available that you can check.

Documentation: http://127.0.0.1:8000/docs/