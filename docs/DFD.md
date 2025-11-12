# Montclair Wardrobe E-Commerce System - Data Flow Diagram

## Overview

This document contains the Data Flow Diagrams (DFD) for the Montclair Wardrobe e-commerce system, showing how data flows through the system at different levels of abstraction.

---

## Context Diagram (Level 0)

The highest level view showing the system as a single process with external entities.

```mermaid
graph TB
    Customer([Customer])
    Seller([Seller])
    Admin([Admin])
    PaymentGateway([Payment Gateway<br/>Airtel/MTN])
    
    System[Montclair Wardrobe<br/>E-Commerce System]
    
    Customer -->|Registration Info<br/>Login Credentials<br/>Product Search<br/>Cart Actions<br/>Order Details<br/>Payment Info<br/>Reviews| System
    System -->|Product Catalog<br/>Order Confirmation<br/>Payment Status<br/>Order Status| Customer
    
    Seller -->|Product Info<br/>Stock Updates<br/>Login Credentials| System
    System -->|Sales Reports<br/>Product Status<br/>Order Notifications| Seller
    
    Admin -->|Approval Decisions<br/>Category Management<br/>User Management| System
    System -->|Pending Approvals<br/>System Reports<br/>User Data| Admin
    
    System -->|Payment Request<br/>Transaction Details| PaymentGateway
    PaymentGateway -->|Payment Confirmation<br/>Transaction Status| System
    
    style System fill:#d4af37,stroke:#333,stroke-width:3px,color:#000
    style Customer fill:#e8f4f8,stroke:#333,stroke-width:2px
    style Seller fill:#e8f4f8,stroke:#333,stroke-width:2px
    style Admin fill:#e8f4f8,stroke:#333,stroke-width:2px
    style PaymentGateway fill:#ffe8e8,stroke:#333,stroke-width:2px
```

---

## Level 1 DFD - Main System Processes

Shows the major processes within the system.

```mermaid
graph TB
    Customer([Customer])
    Seller([Seller])
    Admin([Admin])
    PaymentGateway([Payment Gateway])
    
    P1[1.0<br/>User Management]
    P2[2.0<br/>Product Management]
    P3[3.0<br/>Shopping Cart<br/>Management]
    P4[4.0<br/>Order Processing]
    P5[5.0<br/>Payment Processing]
    P6[6.0<br/>Inventory Management]
    P7[7.0<br/>Review Management]
    
    D1[(User Database)]
    D2[(Product Database)]
    D3[(Cart Database)]
    D4[(Order Database)]
    D5[(Payment Database)]
    D6[(Stock Database)]
    D7[(Review Database)]
    
    Customer -->|Registration/Login| P1
    P1 -->|User Data| D1
    P1 -->|Profile Info| Customer
    
    Seller -->|Product Details| P2
    Admin -->|Approval/Rejection| P2
    P2 -->|Product Data| D2
    P2 -->|Product Status| Seller
    
    Customer -->|Add/Remove Items| P3
    P3 -->|Cart Data| D3
    D2 -->|Product Info| P3
    P3 -->|Cart Summary| Customer
    
    Customer -->|Checkout Request| P4
    D3 -->|Cart Items| P4
    P4 -->|Order Data| D4
    P4 -->|Order Confirmation| Customer
    P4 -->|Stock Update Request| P6
    
    P4 -->|Payment Request| P5
    P5 <-->|Transaction| PaymentGateway
    P5 -->|Payment Data| D5
    P5 -->|Payment Status| P4
    
    P2 -->|Stock Changes| P6
    P4 -->|Stock Reduction| P6
    P6 -->|Stock Data| D6
    P6 -->|Stock Status| P2
    
    Customer -->|Review Submission| P7
    D4 -->|Purchase Verification| P7
    P7 -->|Review Data| D7
    D7 -->|Product Reviews| P2
    
    style P1 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P2 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P3 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P4 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P5 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P6 fill:#b8e6f4,stroke:#333,stroke-width:2px
    style P7 fill:#b8e6f4,stroke:#333,stroke-width:2px
```

---

## Level 2 DFD - Order Processing (Process 4.0)

Detailed view of the order processing workflow.

```mermaid
graph TB
    Customer([Customer])
    
    P41[4.1<br/>Validate Cart]
    P42[4.2<br/>Create Stock<br/>Reservation]
    P43[4.3<br/>Collect Delivery<br/>Information]
    P44[4.4<br/>Calculate Fees]
    P45[4.5<br/>Create Checkout]
    P46[4.6<br/>Process Payment]
    P47[4.7<br/>Create Orders]
    P48[4.8<br/>Update Stock]
    P49[4.9<br/>Send Confirmation]
    
    D3[(Cart Database)]
    D2[(Product Database)]
    D6[(Stock Database)]
    D4[(Order Database)]
    D8[(Checkout Database)]
    
    Customer -->|Checkout Request| P41
    D3 -->|Cart Items| P41
    P41 -->|Validated Items| P42
    
    P42 -->|Reserve Stock| D6
    D2 -->|Stock Availability| P42
    P42 -->|Reservation Confirmed| P43
    
    Customer -->|Delivery Details<br/>Payment Method| P43
    P43 -->|Delivery Info| P44
    
    P44 -->|Location Data| P44
    P44 -->|Calculated Fees| P45
    
    P45 -->|Checkout Data| D8
    P45 -->|Payment Request| P46
    
    P46 -->|Payment Processed| P47
    P47 -->|Order Data| D4
    P47 -->|Stock Update| P48
    
    P48 -->|Reduce Stock| D6
    P48 -->|Stock History| D6
    P48 -->|Complete Reservation| D6
    P48 -->|Orders Created| P49
    
    P49 -->|Confirmation Email<br/>Order Summary| Customer
    
    style P41 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P42 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P43 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P44 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P45 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P46 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P47 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P48 fill:#d4f4dd,stroke:#333,stroke-width:2px
    style P49 fill:#d4f4dd,stroke:#333,stroke-width:2px
```

---

## Level 2 DFD - Product Management (Process 2.0)

Detailed view of product management workflow.

```mermaid
graph TB
    Seller([Seller])
    Admin([Admin])
    Customer([Customer])
    
    P21[2.1<br/>Create/Edit<br/>Product]
    P22[2.2<br/>Upload Images]
    P23[2.3<br/>Set Category]
    P24[2.4<br/>Submit for<br/>Approval]
    P25[2.5<br/>Admin Review]
    P26[2.6<br/>Approve/Reject]
    P27[2.7<br/>Publish Product]
    P28[2.8<br/>Display Products]
    
    D2[(Product Database)]
    D9[(Category Database)]
    D6[(Stock Database)]
    
    Seller -->|Product Details| P21
    P21 -->|Product Data| P22
    P22 -->|Image Upload| P22
    P22 -->|Product with Images| P23
    
    D9 -->|Available Categories| P23
    P23 -->|Categorized Product| P24
    
    P24 -->|Pending Product| D2
    P24 -->|Approval Request| P25
    
    Admin -->|Review Request| P25
    D2 -->|Pending Products| P25
    P25 -->|Product Details| P26
    
    Admin -->|Approval Decision| P26
    P26 -->|Update Status| D2
    P26 -->|Notification| Seller
    P26 -->|Approved Product| P27
    
    P27 -->|Active Product| D2
    P27 -->|Initial Stock| D6
    
    Customer -->|Browse/Search| P28
    D2 -->|Active Products| P28
    P28 -->|Product Catalog| Customer
    
    style P21 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P22 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P23 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P24 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P25 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P26 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P27 fill:#fff4e6,stroke:#333,stroke-width:2px
    style P28 fill:#fff4e6,stroke:#333,stroke-width:2px
```

---

## Level 2 DFD - Payment Processing (Process 5.0)

Detailed view of payment processing workflow.

```mermaid
graph TB
    Customer([Customer])
    PaymentGateway([Payment Gateway<br/>Airtel/MTN])
    
    P51[5.1<br/>Select Payment<br/>Method]
    P52[5.2<br/>Validate Payment<br/>Details]
    P53[5.3<br/>Create Payment<br/>Record]
    P54[5.4<br/>Initiate Payment]
    P55[5.5<br/>Process Gateway<br/>Response]
    P56[5.6<br/>Update Payment<br/>Status]
    P57[5.7<br/>Handle Payment<br/>Failure]
    P58[5.8<br/>Confirm Payment]
    
    D5[(Payment Database)]
    D4[(Order Database)]
    
    Customer -->|Payment Method<br/>Phone Number| P51
    P51 -->|Payment Info| P52
    
    P52 -->|Validated Data| P53
    P53 -->|Payment Record| D5
    P53 -->|Transaction Details| P54
    
    P54 -->|Payment Request| PaymentGateway
    PaymentGateway -->|Response| P55
    
    P55 -->|Success| P56
    P55 -->|Failure| P57
    
    P56 -->|Update Status| D5
    P56 -->|Update Orders| D4
    P56 -->|Success| P58
    
    P57 -->|Error Details| D5
    P57 -->|Retry Option| Customer
    P57 -->|Cancel Orders| D4
    
    P58 -->|Confirmation| Customer
    
    style P51 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P52 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P53 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P54 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P55 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P56 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P57 fill:#ffe6f0,stroke:#333,stroke-width:2px
    style P58 fill:#ffe6f0,stroke:#333,stroke-width:2px
```

---

## Level 2 DFD - Inventory Management (Process 6.0)

Detailed view of inventory/stock management workflow.

```mermaid
graph TB
    Seller([Seller])
    System([System])
    
    P61[6.1<br/>Create Stock<br/>Reservation]
    P62[6.2<br/>Monitor<br/>Reservations]
    P63[6.3<br/>Release Expired<br/>Reservations]
    P64[6.4<br/>Update Stock<br/>Levels]
    P65[6.5<br/>Record Stock<br/>History]
    P66[6.6<br/>Check Stock<br/>Availability]
    P67[6.7<br/>Generate Stock<br/>Alerts]
    
    D6[(Stock Database)]
    D10[(Reservation Database)]
    D11[(Stock History Database)]
    D2[(Product Database)]
    
    System -->|Checkout Started| P61
    P61 -->|Reserve Stock| D10
    D6 -->|Available Stock| P61
    
    P62 -->|Check Expiry| D10
    P62 -->|Expired| P63
    
    P63 -->|Release Stock| D10
    P63 -->|Update Available| D6
    
    System -->|Stock Change| P64
    Seller -->|Restock| P64
    P64 -->|Update Quantity| D6
    P64 -->|Log Change| P65
    
    P65 -->|History Record| D11
    P65 -->|Change Details| D11
    
    System -->|Check Request| P66
    D6 -->|Stock Levels| P66
    D10 -->|Reserved Stock| P66
    P66 -->|Available Quantity| System
    
    P66 -->|Low Stock| P67
    P67 -->|Alert| Seller
    D2 -->|Product Info| P67
    
    style P61 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P62 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P63 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P64 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P65 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P66 fill:#e6f3ff,stroke:#333,stroke-width:2px
    style P67 fill:#e6f3ff,stroke:#333,stroke-width:2px
```

---

## Complete Customer Purchase Flow

End-to-end data flow for a customer making a purchase.

```mermaid
graph TB
    Start([Customer Starts])
    
    A[Browse Products]
    B[Add to Cart]
    C[View Cart]
    D[Proceed to Checkout]
    E[Stock Reservation<br/>Created]
    F[Enter Delivery<br/>Details]
    G[Calculate<br/>Delivery Fee]
    H[Select Payment<br/>Method]
    I[Create Checkout<br/>Record]
    J[Process Payment]
    K{Payment<br/>Successful?}
    L[Create Orders]
    M[Reduce Stock]
    N[Complete<br/>Reservation]
    O[Record Stock<br/>History]
    P[Send Order<br/>Confirmation]
    Q[Clear Cart]
    R[Payment Failed]
    S[Release<br/>Reservation]
    
    End([Order Complete])
    Fail([Payment Failed])
    
    Start --> A
    A -->|Product Data| B
    B -->|Cart Item| C
    C -->|Cart Summary| D
    D -->|Cart Items| E
    E -->|Reserved Stock| F
    F -->|Location Info| G
    G -->|Total Cost| H
    H -->|Payment Method| I
    I -->|Checkout Data| J
    J --> K
    K -->|Yes| L
    K -->|No| R
    L -->|Order Records| M
    M -->|Stock Update| N
    N -->|Reservation Complete| O
    O -->|History Log| P
    P -->|Confirmation| Q
    Q --> End
    R -->|Error Details| S
    S --> Fail
    
    style Start fill:#90EE90,stroke:#333,stroke-width:2px
    style End fill:#90EE90,stroke:#333,stroke-width:2px
    style Fail fill:#FFB6C1,stroke:#333,stroke-width:2px
    style K fill:#FFD700,stroke:#333,stroke-width:2px
    style E fill:#87CEEB,stroke:#333,stroke-width:2px
    style J fill:#87CEEB,stroke:#333,stroke-width:2px
    style M fill:#87CEEB,stroke:#333,stroke-width:2px
```

---

## Data Stores Description

| Data Store | Description | Key Data Elements |
|------------|-------------|-------------------|
| **User Database** | Stores user account information | username, email, password, role, profile data |
| **Product Database** | Stores product catalog | name, description, price, status, approval_status, stock |
| **Category Database** | Stores product categories | name, description, created_by |
| **Cart Database** | Temporary shopping cart data | user_id, product_id, quantity, added_at |
| **Checkout Database** | Checkout session information | user_id, location, payment_method, delivery_fee, status |
| **Order Database** | Individual product orders | user_id, product_id, checkout_id, quantity, status |
| **Payment Database** | Payment transaction records | user_id, method, amount, reference, status |
| **Review Database** | Product reviews and ratings | product_id, user_id, rating, comment, verified |
| **Stock Database** | Current stock levels | product_id, quantity, last_updated |
| **Reservation Database** | Temporary stock reservations | user_id, product_id, quantity, expires_at, status |
| **Stock History Database** | Audit trail of stock changes | product_id, change_type, quantity_change, reason, timestamp |

---

## Data Flow Descriptions

### Main Data Flows

1. **User Registration Flow**
   - Customer → Registration Data → User Management → User Database
   - User Database → Profile Info → Customer

2. **Product Creation Flow**
   - Seller → Product Details → Product Management → Product Database
   - Product Database → Approval Request → Admin
   - Admin → Approval Decision → Product Database

3. **Shopping Flow**
   - Customer → Browse Request → Product Database → Product Catalog → Customer
   - Customer → Add to Cart → Cart Database
   - Cart Database → Cart Summary → Customer

4. **Checkout Flow**
   - Customer → Checkout Request → Order Processing
   - Cart Database → Cart Items → Order Processing
   - Order Processing → Stock Reservation → Stock Database
   - Customer → Delivery Details → Order Processing
   - Order Processing → Payment Request → Payment Processing
   - Payment Processing → Transaction → Payment Gateway
   - Payment Gateway → Confirmation → Payment Processing
   - Payment Processing → Payment Status → Order Processing
   - Order Processing → Create Orders → Order Database
   - Order Processing → Reduce Stock → Stock Database
   - Order Processing → Order Confirmation → Customer

5. **Review Flow**
   - Customer → Review Submission → Review Management
   - Order Database → Purchase Verification → Review Management
   - Review Management → Review Data → Review Database
   - Review Database → Product Reviews → Product Display

6. **Inventory Management Flow**
   - System → Stock Check → Inventory Management
   - Inventory Management → Stock Levels → Stock Database
   - Inventory Management → Stock History → Stock History Database
   - Seller → Restock → Inventory Management

---

## Process Descriptions

### Level 1 Processes

| Process | Name | Description |
|---------|------|-------------|
| **1.0** | User Management | Handles user registration, authentication, profile management |
| **2.0** | Product Management | Manages product creation, editing, approval, and display |
| **3.0** | Shopping Cart Management | Handles adding/removing items, cart display, cart updates |
| **4.0** | Order Processing | Processes checkout, creates orders, manages order lifecycle |
| **5.0** | Payment Processing | Handles payment method selection, processing, confirmation |
| **6.0** | Inventory Management | Manages stock levels, reservations, stock history |
| **7.0** | Review Management | Handles review submission, verification, display |

### Level 2 Processes (Order Processing)

| Process | Name | Description |
|---------|------|-------------|
| **4.1** | Validate Cart | Checks cart items availability and validity |
| **4.2** | Create Stock Reservation | Temporarily reserves stock for checkout |
| **4.3** | Collect Delivery Information | Gathers delivery address and contact details |
| **4.4** | Calculate Fees | Computes delivery fees based on location |
| **4.5** | Create Checkout | Creates checkout record with all details |
| **4.6** | Process Payment | Initiates and processes payment transaction |
| **4.7** | Create Orders | Creates individual order records for each product |
| **4.8** | Update Stock | Reduces stock and completes reservation |
| **4.9** | Send Confirmation | Sends order confirmation to customer |

---

## External Entities

| Entity | Description | Interactions |
|--------|-------------|--------------|
| **Customer** | End users who browse and purchase products | Browse, search, add to cart, checkout, review |
| **Seller** | Users who list products for sale | Create products, manage inventory, view sales |
| **Admin** | System administrators | Approve products, manage categories, manage users |
| **Payment Gateway** | External payment processing services (Airtel Money, MTN Mobile Money) | Process payments, return transaction status |

---

## Key Data Flows Summary

1. **Product Listing**: Seller → Product Data → System → Approval → Admin → Approved Product → Catalog
2. **Shopping**: Customer → Browse → Product Catalog → Add to Cart → Cart Summary
3. **Checkout**: Cart → Validate → Reserve Stock → Collect Info → Calculate Fees → Create Checkout
4. **Payment**: Checkout → Payment Request → Gateway → Confirmation → Order Creation
5. **Order Fulfillment**: Payment Success → Create Orders → Reduce Stock → Confirmation
6. **Review**: Purchase → Verification → Review Submission → Product Rating Update
7. **Inventory**: Stock Changes → History Log → Availability Check → Low Stock Alerts

---

## Notes

- All data flows are validated at each process step
- Stock reservations expire after 15 minutes if checkout is not completed
- Payment failures trigger automatic stock reservation release
- All stock changes are logged in stock history for audit purposes
- Reviews can only be submitted by verified purchasers
- Admin approval is required before products become visible to customers
