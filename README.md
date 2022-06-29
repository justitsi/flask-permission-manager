# permission-manager API
## Overview
The permission manager API provides a simple way to add role and permission based authorization to your project using JWT tokens. It is intended to work with the [jwt_issuer_public](https://github.com/justitsi/jwt_issuer_public) microservice and depends on existing jwt tokens issued by it or following a similiar format.

## How it works
The way this microservice issues authorization tokens is by checking an existing authentication jwt token (called `jwt_token`) and issuing a new token (called `jwt_permissions`) containing role and permission data. This microservice handles roles and permissions by binding permissions to roles and then roles to users:
```
[Permissions] -> [Roles] -> [Users]
```

## Pre-created roles
The permission management microservice pre-creates two roles - `user` and `admin` - to set to users. These two roles have several differences from other roles:

* They cannot be deleted
* Their `roleID`s are always `1` (for `admin`) and `2` (for `user`)

Moreover, the `admin` role:

* Is granted to the first user to authenticate against the permissions API
* Allows for clients to perform CRUD operations on roles and permissions
* Allows to query and manage other user's roles
* Allows granting or removing the `admin` role to other users (users CANNOT remove their own `admin` role, but can manage that role for other users)

The `user` role is automatically assigned to every user upon their first authentication against the permission API

## API Endpoints
All API endpoints require the sender to send a jwt authentication token in order to allow for changes to be made to permissions, roles or users. In addition, all API routes except for `/permission` and `/role` will lookup the user in the database to verify whether they have the `admin` role, which, along with the `user` role, is a special role that is pre-created and cannot be deleted. 

It should be noted that the first user to authenticate against the permission management API will receive the `user` and `admin` roles, and each subsequent user will be granted the `user` role automatically. 

### Authorization endpoint
* `GET` `/auth` - this is the authentication route used for receiving the `jwt_permissions` token. In order to authenticate against the API, clients must send a valid `jwt_token` cookie containg a jwt token issued by the [jwt_issuer_public](https://github.com/justitsi/jwt_issuer_public) microservice.

### Permission management endpoints
The permission-manager API provides full `CRUD` capabilities for permissions registered in the microservice at the following endpoints:

* `GET` `/permission` - returns a list of all permissions
* `GET` `/permission/<id>` - returns information about a single permission
* `POST` `/permission/<id>` - allows for creating new and editing existing permissions. This endpoint expects the request body to follow the following format:
```
{
    "perm_name": string,
    "perm_namePretty": string
}
```
If a POST request is sent to a permission that already exists, the permission with that ID will be overwritten
* `DELETE` `/permission/<id>` - allows for deleting a permission

### Role management endpoints
The permission-manager API provides full `CRUD` capabilities for roles registered in the microservice at the following endpoints:

* `GET` `/role` - returns a list of all roles
* `GET` `/role/<id>` - returns information about a single role
* `POST` `/role/<id>` - allows for creating new and editing existing roles. This endpoint expects the request body to follow the following format:
```
{
    "role_name": string,
    "role_namePretty": string,
    "role_permissions": [int]
}
```
If a POST request is sent to a role that already exists, the role with that ID will be overwritten. The `user` and `admin` roles are an exception to this rule, as their `role_name`s cannot be changed
* `DELETE` `/role/<id>` - allows for deleting a role. The `user` and `admin` roles cannot be deleted

### User management endpoints
* `GET` `/users/all/<pageSize>/<pageNum>` - returns a list of all users registered in the system along with data about their current roles and permissions. The `<pageSize>` and `<pageNum>` paramaters are expected to be positive integers, `<pageSize>` being in the range [1, 200], and `<pageNum>` being smaller than the last page. The data section of this route contains a `nextPage` field, that indicates whether a page after the current one exists.

* `GET` `/users/byRole/<roleID>` - returns role infomration as well as a list of users that have that role within the permission management system. The `<roleID>` URL paramater should be an integer and a valid id of a `role` within the system

* `POST` `/users/bind/<roleID>` - allows for adding and removing a role to multiple users. The `<roleID>` URL paramater should be an integer and a valid id of a `role` within the system. This route expects a request body of the following format:
```
{
    "action": string,
    "users": [int]
}
```
Where, `action` is either `add` or `remove` for adding or removing the specified role to the list of users, and `users` is a list of integers that are valid `userID`s. In case a specific `userID` is invalid, the changes will not be attempted on that user. It should be noted that when attempting to remove the `admin` role, the client making the change will not be able to remove the `admin` role from their own `user` entry. 

* `POST` `/users/register` - this endpoint is used for mass registering users by id. It acceptrs an array of `userIDs` and registeres all of them with the default `user` role in the system. The `POST` request body should follow the format:
```
{
	"users":[int]
}
``` 
Where `users` is an array of user IDs. It should be noted that only logged in users registered as an `admin` can perform this action.*Users already registered in the system will not be re-registered!* - if a supplied `userID` belongs to a `user` registered in the sytem, they will not be affected.

* `POST` `/user/unregister` - allows for deleting user entries from the system. This route expects a request body of the following format:
```
{
    "users": [int]
}
```
Where `users` is a list of integers that are valid `userID`s. In case a specific `userID` is invalid, the changes will not be attempted on that user. It should be noted that any `user` that has the `admin` role will remain unaffected by changes attempted by using this route.


## Token formats
This microservice operates on two different jwt tokens: it checks the `jwt_token` authentication token issued by the [jwt_issuer_public](https://github.com/justitsi/jwt_issuer_public) microservice and issues a `jwt_permissions` providing role and permission data. The formats of the tokens is as follows:

```
jwt_token:{
    "userID": int
    "issued": DateTime string
    "expires": DateTime string
}
```

```
jwt_permissions:{
    "permissions":[
        permissionID<int>:{
            "id": int
            "name": string
            "namePretty": string
        }
    ]
    "roles":[
        roleID<int>:{
            "id": int
            "name": string
            "namePretty": string
        }
    ]
    "userID": int
    "issued": DateTime string
}
```

## Development
The development server can be run by running the following command in the root directory of this repository: 

```
$ python src/main.py
```

It should be noted that the microservice needs a instance of the `Postgres` database reachable at `localhost:5432` with a username, password and database name set as `postgres`. These settings can be adjusted by editing the `src/.env` file. A databse running with those settings, along with a management interface (reachable at `http://localhost:5080/`) can be brought up by running the following command in the root of this repository:

```
$ docker-compose up
```

## Deploying to production
This repository provides a `Dockerfile` to create a container running the API. The default port for serving API connections for the container is `8082`. For more information on deploying the API please see the included `docker-compose.yml` file at the root of the repository. As database connection settings are stored in an .env file, please edit the `static_files/prod.env` file before building the container. Alternatevly, a `.env` file can be mounted to `/project/src/.env` inside the container to overwrite the baked `.env` file.
