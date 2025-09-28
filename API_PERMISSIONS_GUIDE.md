# API Permission Testing Guide

## Overview
This document outlines the API permission restrictions implemented to ensure that only appropriate users can access vendor-specific endpoints.

## Changes Made

### 1. Custom Permission Classes Created (`core/permissions.py`)

#### `IsVendorOrReadOnly`
- **Purpose**: Controls access to vendor creation and management endpoints
- **Read Access**: Any authenticated user can view vendor information
- **Write Access**: 
  - Create: Only users without existing vendor accounts can create new vendor accounts
  - Update/Delete: Only the vendor owner (or superuser) can modify their account

#### `IsVendorOwnerOrReadOnly`
- **Purpose**: Controls access to product creation and management endpoints
- **Read Access**: Any authenticated user can view products
- **Write Access**:
  - Create: Only existing vendors can create products
  - Update/Delete: Only the vendor who owns the product (or superuser) can modify it

#### `IsOwnerOrReadOnly`
- **Purpose**: General permission for object ownership
- **Read Access**: Anyone can read
- **Write Access**: Only the object owner (or superuser) can modify

### 2. API ViewSet Updates

#### `VendorViewSet`
- **Permission Class**: `IsVendorOrReadOnly`
- **Enhanced Validation**: 
  - Prevents users with existing vendor accounts from creating new ones
  - Prevents users already marked as vendors in their profile from creating duplicate accounts
  - Properly manages user groups and profile updates
- **New Methods**:
  - `perform_update()`: Ensures only owner can update their vendor account
  - `perform_destroy()`: Ensures only owner can delete their vendor account, automatically reverts user back to buyer status

#### `ProductViewSet`
- **Permission Class**: `IsVendorOwnerOrReadOnly`
- **Enhanced Validation**: Clearer error message when non-vendors try to create products

## API Endpoint Behavior

### Vendor Endpoints (`/api/v1/vendors/`)

| Method | Endpoint | Permission Required | Behavior |
|--------|----------|-------------------|----------|
| GET | `/api/v1/vendors/` | Authenticated user | List all vendors |
| POST | `/api/v1/vendors/` | Authenticated user without existing vendor account | Create new vendor account |
| GET | `/api/v1/vendors/{id}/` | Authenticated user | View specific vendor |
| PUT/PATCH | `/api/v1/vendors/{id}/` | Owner of vendor account or superuser | Update vendor account |
| DELETE | `/api/v1/vendors/{id}/` | Owner of vendor account or superuser | Delete vendor account |

### Product Endpoints (`/api/v1/products/`)

| Method | Endpoint | Permission Required | Behavior |
|--------|----------|-------------------|----------|
| GET | `/api/v1/products/` | Authenticated user | List all products |
| POST | `/api/v1/products/` | Authenticated user with vendor account | Create new product |
| GET | `/api/v1/products/{id}/` | Authenticated user | View specific product |
| PUT/PATCH | `/api/v1/products/{id}/` | Vendor owner of product or superuser | Update product |
| DELETE | `/api/v1/products/{id}/` | Vendor owner of product or superuser | Delete product |

## Error Messages

### Vendor Creation Errors
- `"You already have a vendor account."` - User already has a vendor account
- `"Your profile indicates you are already a vendor."` - User profile shows vendor type but no vendor account exists

### Product Creation Errors
- `"Only vendors can create products. Please register as a vendor first."` - Non-vendor trying to create product

### Permission Errors
- `"You can only update your own vendor account."` - User trying to update someone else's vendor account
- `"You can only delete your own vendor account."` - User trying to delete someone else's vendor account

## Testing Scenarios

### Scenario 1: Buyer trying to create vendor account via API
1. **Expected**: SUCCESS - Buyer should be able to create vendor account
2. **Result**: User becomes vendor, profile updated, groups changed, Twitter notification sent

### Scenario 2: Existing vendor trying to create another vendor account via API
1. **Expected**: ERROR - "You already have a vendor account."
2. **Result**: 403 Forbidden

### Scenario 3: Buyer trying to create product via API
1. **Expected**: ERROR - "Only vendors can create products. Please register as a vendor first."
2. **Result**: 403 Forbidden

### Scenario 4: Vendor trying to create product via API
1. **Expected**: SUCCESS - Product created and associated with vendor
2. **Result**: Product created, Twitter notification sent

### Scenario 5: User trying to update another user's vendor account
1. **Expected**: ERROR - "You can only update your own vendor account."
2. **Result**: 403 Forbidden

### Scenario 6: User trying to delete another user's vendor account
1. **Expected**: ERROR - "You can only delete your own vendor account."
2. **Result**: 403 Forbidden

## Security Benefits

1. **Access Control**: Only appropriate users can perform specific actions
2. **Data Integrity**: Prevents users from modifying other users' accounts or products
3. **Role Enforcement**: Maintains proper separation between buyer and vendor roles
4. **Audit Trail**: All actions are logged with user information
5. **Automatic Cleanup**: When vendor accounts are deleted, user profiles are properly reverted

## Integration with Web Interface

The permission system works alongside the existing web interface permissions:
- Web forms use Django's built-in permission system and mixins
- API uses Django REST Framework permission classes
- Both systems maintain consistent business logic and user role management