# Freelance Market

## Overview

RepairMasters is a dynamic freelance market designed for skilled repair professionals and clients in need of their services. The platform facilitates seamless connections between clients and repair masters, offering a variety of features to enhance the user experience.

## Tech Stack

- **Python 3.10:** The backbone of our project, ensuring efficient and powerful functionality.
- **FastAPI:** A modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Celery:** Distributed task queue for handling asynchronous processes and background tasks.
- **PostgreSQL:** A powerful, open-source relational database system.
- **SQLAlchemy:** A SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **Docker:** Containerization technology to ensure easy deployment and scalability.

## Key Features

1. **User Roles:**
   - **Client:** Users seeking repair services.
   - **Master:** Skilled professionals providing repair services.

2. **Connection Options:**
   - Clients can connect with repair masters through direct orders or by posting freelance requests.

3. **Payment Integration:**
   - Integration with YooMoneyAPI for seamless balance management, ensuring secure and convenient transactions.

4. **Security Measures:**
   - Email and phone number verification for enhanced user security.

5. **Feedback Systems:**
   - Robust order-feedback system for clients to share their experiences.
   - User reviews system to build trust within the RepairMasters community.

6. **Content Management:**
   - Article system for sharing valuable information and updates.

7. **Admin Panel:**
   - Custom admin panel providing access to all project data and settings.

## Getting Started

To run the RepairMasters project locally, follow these steps:

1. Clone the repository.
2. Install the required dependencies using the provided `requirements.txt` file.
3. Set up and configure the PostgreSQL database.
4. Update the configuration files for YooMoneyAPI integration.
5. Run the FastAPI server and Celery workers.

For detailed instructions, refer to the project documentation.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
