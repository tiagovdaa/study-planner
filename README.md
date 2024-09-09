# Study Planner

The **Study Planner** is a web application that allows users to upload CSV files containing a list of courses and/or books, define study effort percentages, set available study time for each day, and generate a study schedule. The schedule can be downloaded as a CSV,Google Calendar or iCalendar (ICS), or PDF.

## Features

- Upload CSV file containing courses or books with duration (for courses) or number of pages (for books).
- Allocate effort percentages for each course/book.
- Define availability slots for study time for each day of the week.
- Generate a study schedule, which can be downloaded as:
  - CSV
  - Google / iCalendar (ICS)
  - PDF with a table format showing the study plan.
  
## Prerequisites

Before running the project, make sure you have the following installed:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Project Setup

This project is Dockerized, and you can use Docker or Docker Compose to build and run the application.

### Project Structure

```
|-- app.py                     # Main application logic
|-- requirements.txt           # required python libs.
|-- templates    
    |-- index.html             # HTML template for the web 
|-- Dockerfile                 # Dockerfile to build the app
|-- docker-compose.yml         # Docker Compose configuration
|-- sample.csv/                # A sample CSV file 
```

### CSV File Format

Your CSV file should have the following format:

```
name,type,duration_hours,total_pages
Kubernetes,course,35,
AWS,course,40,
Cloud Strategy Book,,450
```

- **name**: The name of the course or book.
- **type**: Can be either "course" or "book".
- **duration_hours**: For courses, specify the total duration in hours.
- **total_pages**: For books, specify the total number of pages (if applicable).

## Building and Running with Docker

### Step 1: Clone the Repository

```bash
git clone https://github.com/tiagovdaa/study-planner.git
cd study-planner
```

### Step 2: Build the Docker Image

You can build the Docker image using the following command:

```bash
docker build -t study-planner .
```

### Step 3: Run the Application

After building the Docker image, you can run the container using:

```bash
docker run -d -p 5000:5000 --name study-planner study-planner
```

This will run the application in a Docker container, and you can access the application by visiting `http://localhost:5000` in your browser.

## Building and Running with Docker Compose

To simplify the process, you can use **Docker Compose** to build and run the application.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/study-planner.git
cd study-planner
```

### Step 2: Build and Run with Docker Compose

Run the following command to build and start the application using Docker Compose:

```bash
docker-compose up --build
```

This will automatically build the image, create the container, and start the application. The application will be available at `http://localhost:5000`.

### Step 3: Stop the Application

To stop the application, run:

```bash
docker-compose down
```

## General Usage

1. **Upload CSV**: Start by uploading a CSV file containing your list of courses and/or books.

2. **Allocate Effort**: After the CSV is loaded, allocate effort percentages for each course (e.g., 60% for Course A, 30% for Course B, and 10% for Book C). Ensure the total effort is 100%.

3. **Set Availability**: Set your available study slots for each day (e.g., Monday 6 pm to 9 pm, Tuesday 7 pm to 10 pm, etc.).

4. **Select File Type**: Choose the file type you want for your schedule (Google Calendar CSV, iCalendar ICS, or PDF).

5. **Generate Schedule**: Click "Generate Calendar" to create your study schedule and download the file.

## Accessing the Application

Once the Docker container is running, open your web browser and navigate to:

```
http://localhost:5000
```

Here you can:
- Upload your CSV.
- Set study preferences.
- Generate and download your study schedule.

## Troubleshooting

- If you encounter any errors, ensure Docker and Docker Compose are installed correctly.
- Check if any ports (like `5000`) are already in use on your system and modify the port in the `docker-compose.yml` or `docker run` command if necessary.