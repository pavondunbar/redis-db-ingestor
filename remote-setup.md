# **Setup of New Database Connection to Scanner Front End**

## **Overview**

This document details the process undertaken to set up a new database connection for the scanner front end, utilizing a Redis-based cache mechanism alongside a PostgreSQL database. This setup replaces the old system, which previously ingested data directly. The new infrastructure is designed to improve performance, scalability, and maintainability.

---

## **1. Remote Server Access**

### **1.1. Secure Shell (SSH) Login**
The first step involved accessing the remote server where both the database and scanner front end are hosted. This was achieved using the SSH protocol:

```bash
ssh username@remote-server-ip
```

- **username**: The user account on the remote server.
- **remote-server-ip**: The IP address of the server hosting the applications.

### **1.2. Verification**
Upon successful login, the server's status and environment were verified to ensure all necessary tools and services were available.

---

## **2. Redis Installation and Configuration**

### **2.1. Installation**
Redis was not previously installed on the server, so it was installed via the following commands:

```bash
sudo apt update
sudo apt install redis-server
```

### **2.2. Configuration**
The Redis configuration file was then accessed and modified to ensure secure and optimal operation:

```bash
sudo nano /etc/redis/redis.conf
```

Key changes included:
- **bind**: Configured to `127.0.0.1` to allow only local connections, enhancing security.
- **protected-mode**: Set to `yes` to protect against unauthorized access.
- **requirepass**: A strong password was set to secure Redis operations.

```ini
bind 127.0.0.1
protected-mode yes
requirepass YourStrongPassword
```

### **2.3. Restarting Redis**
After making the necessary changes, Redis was restarted to apply the new configuration:

```bash
sudo systemctl restart redis
```

Redis was verified to be running correctly with:

```bash
sudo systemctl status redis
```

---

## **3. PostgreSQL Installation and Redis Integration**

### **3.1. PostgreSQL Installation**
PostgreSQL, along with its necessary extensions, was installed to manage the relational data:

```bash
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-server-dev-all
sudo apt-get install postgresql-redis
```

### **3.2. Database and User Setup**
A new PostgreSQL database was created for the scanner front end, and appropriate user privileges were set up:

```bash
sudo -u postgres psql
CREATE DATABASE your_database_name;
CREATE USER your_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_user;
```

### **3.3. Configuring Redis Triggers**
The PostgreSQL database was configured to push updates to Redis using triggers. A function was created within PostgreSQL to notify Redis whenever data changes occurred:

```sql
CREATE OR REPLACE FUNCTION notify_redis() RETURNS trigger AS $$
BEGIN
    PERFORM redis_command('SET', NEW.id, NEW.data);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

This function was then linked to a trigger, ensuring that any changes to the `example_table` would be communicated to Redis:

```sql
CREATE TRIGGER example_trigger
AFTER INSERT OR UPDATE ON example_table
FOR EACH ROW EXECUTE FUNCTION notify_redis();
```

---

## **4. Front-End Configuration**

### **4.1. Configuration File Updates**
The scanner front end’s configuration files were updated to connect to the new database and Redis setup. This included updating connection strings and ensuring the application code was compatible with the new cache mechanism.

For instance, the `.env` file was updated as follows:

```ini
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_database_name
REDIS_URL=redis://localhost:6379
```

### **4.2. Verification of Connections**
To confirm that the front end was correctly communicating with both Redis and PostgreSQL, several test queries were run. This included verifying data flows from PostgreSQL to Redis and ensuring the front-end application could retrieve this data.

---

## **5. Testing and Monitoring**

### **5.1. Initial Testing**
The front-end application was restarted, and its functionality was tested thoroughly. Testing included:

- **Database connectivity**: Ensuring the application could query and display data from PostgreSQL.
- **Redis caching**: Verifying that data changes were reflected in Redis and that the front-end could retrieve cached data efficiently.

### **5.2. Log Monitoring**
Application logs were monitored in real-time to detect any errors or performance issues:

```bash
tail -f /var/log/scanner-frontend.log
```

### **5.3. Performance Monitoring**
System performance was monitored over time to ensure the new setup was stable and performed as expected under different loads.

---

## **6. Documentation and Communication**

### **6.1. Process Documentation**
All changes, configurations, and procedures were documented to ensure that future maintenance or further modifications could be performed with ease. This documentation includes:

- **Installation steps**: For Redis and PostgreSQL.
- **Configuration details**: For the Redis setup, PostgreSQL triggers, and front-end connections.
- **Testing procedures**: Describing how the connection was verified and what tests were conducted.

### **6.2. Team Communication**
The team was informed of the changes, including any new credentials, configuration changes, and where to find the updated documentation. This ensured everyone was aligned with the new infrastructure.
