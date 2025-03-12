# Assignment 3: Inventory Management System

## Part 1: Project Plan

### Description
The Inventory Management System is designed to support with inventory control for small businesses and warehouses. It features a centralized platform for tracking stock levels, managing supplier information and processing orders efficiently. With user-friendly interfaces and robust CRUD functionalities, the system aims to reduce overall manual errors and support informed decision making. 

### Main Features
- CRUD Operations:
    - Create, Read, Update, Delete functionalities for inventory items
    - CRUD operations for managing suppliers and cetegories

- User Interface
    - A modern web interface for managing items and viewing inventory
    - A simple and intutive dashboard to display stock levels and alerts

- Authentication & Authorization
    - User registration, login, and role-based access

- Search and Pagenation
    - Ability to search items based on name, category, or supplier
    - List view with pagination for easy browsing

- Time-Permitting Features
    - Real time updates on inventory changes
    - Reporting and analytics features 


### Database Schema Design (ERD)
![ERD Diagram](ERD-Image.png)

### API Endpoints Structure 
### Inventory Items
List all inventory items.
```bash
GET /items
```
Retrieve details for a single inventory item.
```bash
GET /items/{item_id}
```
Create a new inventory item.
```bash
POST /items
```
Update an existing inventory item.
```bash
POST /items/{item_id}
```
Remove an inventory item from the system.
```bash
DELETE /items/{item_id}
```
---
### Suppliers
 List all suppliers.
 ```bash
GET /suppliers
 ```
 Adding suppliers
 ```bash
POST /suppliers
 ```
---
### Categories
List all categories
```bash
GET /categories
```
Create new categories
```bash
POST /categories
```
---
### User Authentication
Register a new user
```bash
POST /auth/register
```
Log in an existing user
```bash
POST /auth/login
```
Get profile of logged-in user
```bash
GET /auth/profile
```