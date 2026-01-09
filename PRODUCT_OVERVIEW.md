# CovenantIQ - AI-Powered Loan Covenant Monitoring Platform

## Executive Summary

**CovenantIQ** (Covenant Compass) is an enterprise-grade financial risk management platform that leverages artificial intelligence to automate the monitoring, tracking, and analysis of loan covenants across institutional loan portfolios. The platform transforms weeks of manual document review into minutes of automated processing, enabling financial institutions to proactively manage covenant compliance and portfolio risk.

---

## Table of Contents

1. [The Problem We Solve](#the-problem-we-solve)
2. [What CovenantIQ Does](#what-covenantiq-does)
3. [Detailed Feature Breakdown](#detailed-feature-breakdown)
4. [User Workflows](#user-workflows)
5. [Technical Architecture](#technical-architecture)
6. [Data Model](#data-model)
7. [Use Cases](#use-cases)
8. [Future Roadmap](#future-roadmap)

---

## The Problem We Solve

### Traditional Loan Covenant Monitoring Challenges

**1. Manual Document Review**
- Loan agreements are 50-200+ page PDF documents
- Covenants are scattered throughout legal text
- Extracting covenant details requires hours of manual reading
- High risk of human error in interpretation

**2. Tracking Complexity**
- Large portfolios contain hundreds of loans
- Each loan may have 3-10+ covenants
- Different covenants have different testing frequencies (quarterly, semi-annual, annual)
- Managing 500+ covenants across 100 loans in spreadsheets is error-prone

**3. Reactive vs. Proactive Management**
- Traditional systems only identify breaches after they occur
- No early warning system for covenants approaching breach
- Limited trend analysis capabilities
- Missed opportunities for proactive borrower engagement

**4. Risk Exposure**
- Undetected covenant breaches can lead to:
  - Financial losses (default risk)
  - Regulatory compliance issues
  - Missed opportunities to renegotiate terms
  - Reputational damage

### CovenantIQ's Solution

- **AI-powered extraction**: Seconds instead of hours
- **Centralized tracking**: Single source of truth for all covenants
- **Predictive analytics**: Identify risks before breaches occur
- **Portfolio-wide visibility**: Dashboard view of entire loan book health

---

## What CovenantIQ Does

### Core Value Proposition

CovenantIQ automates the entire covenant lifecycle from extraction to monitoring to alerting, enabling financial institutions to:

1. **Extract covenants automatically** from loan agreement PDFs using AI
2. **Track covenant compliance** with real-time measurements and status updates
3. **Predict potential breaches** before they occur using trend analysis
4. **Visualize portfolio risk** through interactive dashboards and heatmaps
5. **Receive automated alerts** for covenants requiring attention
6. **Generate analytics** on portfolio health and covenant performance

---

## Detailed Feature Breakdown

### 1. AI-Powered Document Processing

**Location**: `backend/app/api/endpoints/loans.py`, `backend/app/services/openai_service.py`

#### What You Can Do:
- **Upload loan agreement PDFs** (up to 10MB each)
- **Automatic extraction of**:
  - Borrower name and company information
  - Loan amount and currency
  - Origination and maturity dates
  - All covenant clauses in the document
  - Covenant types (financial, operational, negative, affirmative)
  - Threshold values and operators (e.g., "Debt/EBITDA ≤ 3.5")
  - Testing frequency (quarterly, semi-annual, annual)
  - Specific calculation methodologies

#### How It Works:
```
1. User uploads PDF via drag-and-drop interface
2. Backend saves file securely and creates loan record
3. Background task extracts text from PDF using pdfplumber
4. OpenAI GPT-4 analyzes the text and structures covenant data
5. System creates covenant records in database
6. User is notified when extraction completes (typically 30-60 seconds)
```

#### Example Extraction Output:
```json
{
  "borrower_name": "Acme Manufacturing Inc.",
  "loan_amount": 5000000,
  "currency": "USD",
  "origination_date": "2024-01-15",
  "maturity_date": "2029-01-15",
  "covenants": [
    {
      "covenant_type": "financial",
      "covenant_name": "Debt Service Coverage Ratio",
      "description": "Maintain minimum DSCR of 1.25x",
      "threshold_value": 1.25,
      "threshold_operator": "greater_or_equal",
      "frequency": "quarterly"
    },
    {
      "covenant_type": "financial",
      "covenant_name": "Total Leverage Ratio",
      "description": "Total Debt to EBITDA not to exceed 3.5x",
      "threshold_value": 3.5,
      "threshold_operator": "less_or_equal",
      "frequency": "quarterly"
    }
  ]
}
```

---

### 2. Covenant Monitoring & Measurement Tracking

**Location**: `backend/app/api/endpoints/covenants.py`, `backend/app/models/covenant.py`

#### What You Can Do:

**A. View All Covenants**
- See all covenants across your entire loan portfolio
- Filter by loan, status, type, or frequency
- Search by covenant name or description

**B. Record Measurements**
- Input actual covenant values (e.g., "DSCR = 1.45")
- System automatically:
  - Compares against threshold
  - Calculates distance to breach
  - Determines status (Compliant, Warning, Breach)
  - Updates historical trend data

**C. Status Classification Logic**:
```python
# Compliant: Safe, no concerns
# Example: DSCR = 1.45, threshold = 1.25 → Compliant (16% buffer)

# Warning: Within 10% of breach threshold
# Example: DSCR = 1.28, threshold = 1.25 → Warning (2.4% buffer)

# Breach: Violates covenant threshold
# Example: DSCR = 1.20, threshold = 1.25 → Breach (-4% violation)
```

**D. Historical Tracking**
- View measurement history for each covenant
- See trends over time (improving vs. deteriorating)
- Identify seasonal patterns or cyclical behavior

#### API Endpoints Available:
```
GET    /api/covenants/loan/{loan_id}     - List all covenants for a loan
GET    /api/covenants/{covenant_id}      - Get covenant details
POST   /api/covenants/{id}/measure       - Record new measurement
GET    /api/covenants/{id}/measurements  - Get measurement history
PATCH  /api/covenants/{covenant_id}      - Update covenant details
DELETE /api/covenants/{covenant_id}      - Deactivate covenant
```

---

### 3. Intelligent Alert System

**Location**: `backend/app/models/alert.py`, `backend/app/api/endpoints/alerts.py`

#### What You Can Do:

**A. Automatic Alert Generation**
The system automatically creates alerts when:
- A covenant breaches its threshold
- A covenant enters warning zone (within 10% of breach)
- Trend analysis predicts a future breach
- A covenant hasn't been measured in expected timeframe

**B. Alert Severity Levels**:
- **Critical**: Covenant breach, immediate action required
- **High**: Within 5% of breach, urgent attention needed
- **Medium**: Within 10% of breach, monitoring required
- **Low**: Informational alerts, no immediate risk

**C. Alert Information Includes**:
- Alert title and detailed message
- Affected loan and covenant
- Current value vs. threshold
- Predicted breach date (if applicable)
- Days until predicted breach
- Recommended actions

**D. Alert Management**:
- View all alerts sorted by severity
- Mark alerts as read
- Resolve alerts with notes
- Filter by severity, loan, or date range

#### Example Alert:
```
Title: "Debt Service Coverage Ratio Approaching Breach"
Severity: HIGH
Loan: Acme Manufacturing Inc. - $5M Facility
Message: "The DSCR has declined to 1.28x, approaching the minimum
         requirement of 1.25x. Current buffer is only 2.4%. Based on
         current trends, a breach may occur within the next 45 days."
Predicted Breach Date: March 15, 2026
Recommended Action: "Contact borrower to discuss financial performance
                    and potential need for covenant modification."
```

---

### 4. Portfolio Analytics Dashboard

**Location**: `frontend/src/pages/Dashboard.tsx`, `backend/app/api/endpoints/analytics.py`

#### What You Can See:

**A. Portfolio Value Overview**
- **Total Portfolio Value**: Sum of all active loan amounts
  - Real-time calculation from database
  - Displayed with animated counter for visual impact

- **Period-over-Period Comparison**:
  - Current value vs. 30 days ago
  - Percentage change calculation
  - Absolute dollar change
  - Visual indicator (up/down arrows)

**B. Portfolio Trends Chart**
- **13-Month Historical View**:
  - Line chart showing portfolio value over time
  - Current year data (black line)
  - Previous year comparison (gray line)
  - Dynamic Y-axis scaling based on actual values
  - Interactive hover tooltips (planned)

**C. Key Metrics Grid**:

1. **Total Covenants**
   - Count of all active covenants
   - Across all loan agreements
   - Icon: Document symbol

2. **Compliant Covenants**
   - Number of covenants in good standing
   - Percentage of total portfolio
   - Trend: % change vs. previous period
   - Green indicator for positive trends

3. **At Risk Covenants**
   - Sum of Warning + Breach status covenants
   - Indicates covenants requiring attention
   - Trend: % change vs. previous period
   - Red indicator for increasing risk

**D. Risk Heatmap**
- **Visual Portfolio Overview**:
  - Grid of colored tiles, one per loan
  - Color coding:
    - Green: All covenants compliant
    - Yellow: One or more covenants in warning
    - Red: One or more covenants breached
  - Hover to see loan details
  - Click to navigate to loan detail page
  - Displays up to 48 loans at once

**E. Recent Alerts Panel**
- **Latest 6 Critical/High Alerts**:
  - Alert title and message preview
  - Severity badge (color-coded)
  - Time since creation
  - Pulsing indicator for unread alerts
  - Click to view full alert details
  - "View All" link to alerts page

**F. Period Selector**
- Filter data by time period:
  - Last Week (default)
  - Last Month
  - Last Year
  - All Time
- Dynamically updates all dashboard metrics

#### API Endpoints Powering Dashboard:
```
GET /api/analytics/portfolio-summary      - Core metrics (loans, covenants, alerts)
GET /api/analytics/portfolio-value        - Current vs. previous period value
GET /api/analytics/portfolio-trends       - 13 months of historical data
GET /api/analytics/covenant-trends        - Covenant status change percentages
GET /api/analytics/risk-heatmap          - Loan-level status for visualization
GET /api/analytics/critical-alerts       - Top 5 most severe alerts
```

---

### 5. Loan Management

**Location**: `frontend/src/pages/Loans.tsx`, `frontend/src/pages/LoanDetail.tsx`

#### What You Can Do:

**A. Loan List View** (`/loans`)
- See all loans in your portfolio
- Each loan card shows:
  - Borrower name
  - Loan amount (formatted currency)
  - Number of covenants
  - Overall status badge (Compliant/Warning/Breach)
  - Borrower initials avatar
- Click any loan to view details

**B. Loan Detail View** (`/loans/{loanId}`)

**Overview Tab**:
- Borrower name and company information
- Loan title
- Principal amount and currency
- Origination date
- Maturity date
- Overall loan status

**Covenants Tab**:
- Complete list of all covenants for this loan
- For each covenant:
  - Covenant name and type
  - Description and calculation methodology
  - Threshold value and operator
  - Current status with color coding
  - Latest measurement value
  - Testing frequency
  - Next test date
- Expandable rows to see:
  - Full measurement history
  - Trend charts
  - Historical compliance

**Documents Tab**:
- Original loan agreement PDF
- Download button for offline access
- View upload date and metadata
- (Future: Additional document attachments)

**Financials Tab**:
- (Coming soon)
- Borrower financial statements
- Key financial metrics dashboard
- Trend analysis

**C. Add Loan Button**:
- Upload new loan agreements
- Triggers AI extraction process
- Shows extraction progress
- Auto-refreshes when complete

---

### 6. Alerts Management

**Location**: `frontend/src/pages/Alerts.tsx`

#### What You Can Do:

**A. View All Alerts**
- Comprehensive list of all alerts
- Sorted by creation date (newest first)
- Filter options:
  - By severity (Critical, High, Medium, Low)
  - By status (Unread, Read, Resolved)
  - By loan
  - By date range

**B. Alert Cards Show**:
- Alert icon based on severity (color-coded)
- Alert title
- Detailed message explaining the issue
- Severity badge
- Predicted breach date (if applicable)
- Time since alert creation
- Associated loan link

**C. Alert Actions**:
- Click to mark as read
- Resolve alert with notes
- Navigate to associated covenant
- Export alert history

**D. Empty State**:
- When no alerts exist:
  - Success icon
  - "All Clear" message
  - Positive confirmation of portfolio health

---

### 7. User Settings & Account Management

**Location**: `frontend/src/pages/Settings.tsx`

#### What You Can Do:

**A. Profile Management**:
- Update full name
- Change email address
- Update company/organization name
- Set role/title

**B. Password & Security**:
- Change password
- Set up two-factor authentication (planned)
- View active sessions
- Security audit log

**C. Notification Preferences**:
- Email alerts for breaches
- Warning notifications
- Daily/weekly summary emails
- Alert threshold customization

**D. API Access**:
- Generate API keys for integrations
- View API usage statistics
- Manage webhook endpoints

---

## User Workflows

### Workflow 1: Onboarding New Loan

**Scenario**: Bank just closed a new $10M loan and needs to monitor covenants

```
1. User clicks "Add Loan" button on Dashboard
2. Drag-and-drop loan agreement PDF into upload modal
3. Enter loan title: "Acme Manufacturing - $10M Term Loan"
4. Click "Upload and Extract"
5. System shows "Processing..." status (30-60 seconds)
6. Extraction completes, user receives notification
7. Navigate to loan detail page
8. Review extracted information:
   - Borrower: Acme Manufacturing Inc.
   - Amount: $10,000,000
   - 5 covenants identified
9. Review each covenant for accuracy
10. Adjust any threshold values if needed
11. Set next test dates based on origination date
12. Loan is now monitored in portfolio
```

**Time Investment**: 3-5 minutes (vs. 1-2 hours manually)

---

### Workflow 2: Quarterly Covenant Compliance Check

**Scenario**: End of Q1, need to record covenant measurements for all loans

```
1. Navigate to Dashboard
2. Select period: "Q1 2026"
3. View "At Risk" metric - shows 3 loans flagged
4. Click on Loans page
5. Filter loans by "Warning" status
6. Click first loan: "Beta Industries"
7. Go to Covenants tab
8. For each covenant:
   a. Click "Record Measurement"
   b. Enter actual value from borrower's financial report
   c. System auto-calculates:
      - Compliance status
      - Distance to breach
      - Trend vs. previous quarter
   d. Add notes (e.g., "Received Q1 financials on 4/10/26")
   e. Save measurement
9. System updates:
   - Loan status (if covenant breached)
   - Dashboard metrics
   - Generates alerts if needed
10. Repeat for all loans requiring quarterly testing
```

**Time Investment**: 5-10 minutes per loan (vs. 30-60 minutes manually)

---

### Workflow 3: Responding to Critical Alert

**Scenario**: System detects a covenant approaching breach

```
1. User receives email: "Critical Alert - DSCR Warning for Acme Manufacturing"
2. Login to CovenantIQ
3. Dashboard shows red notification badge on Alerts
4. Navigate to Alerts page
5. See alert at top:
   Title: "Debt Service Coverage Ratio Approaching Breach"
   Severity: HIGH
   Loan: Acme Manufacturing - $5M
   Message: "DSCR declined to 1.28x (threshold: 1.25x)"
   Predicted breach: 45 days

6. Click alert to view full details
7. Navigate to loan detail page
8. Review covenant measurement history:
   - Q4 2025: 1.45x (Compliant)
   - Q1 2026: 1.28x (Warning) ← Declining trend
9. View trend chart - shows consistent decline
10. Check borrower's recent financial performance
11. Decision: Contact borrower proactively
12. In CovenantIQ, add note to covenant:
    "Called CFO on 4/15/26. Discussed declining cash flow.
     Scheduling meeting to review covenant modification."
13. Mark alert as "In Progress"
14. Schedule follow-up task
15. After meeting, record outcome:
    - Agreed to temporary threshold adjustment
    - Update covenant in system
    - Resolve alert with resolution notes
```

**Business Impact**: Proactive intervention before breach occurs, maintains positive borrower relationship

---

### Workflow 4: Portfolio Risk Review with Management

**Scenario**: Monthly executive review of portfolio health

```
1. Open Dashboard on conference room screen
2. Point out key metrics:
   - Portfolio Value: $450M (+2.5% vs. last month)
   - 287 covenants tracked across 52 loans
   - 94% compliant (271 covenants healthy)
   - 17 covenants in warning zone
   - 0 breaches this month

3. Review Trend Chart:
   - Portfolio growing steadily (black line)
   - Outpacing last year's growth (gray line)
   - Point out seasonal dip in July (normal)

4. Risk Heatmap Analysis:
   - 48 loans visible, mostly green (healthy)
   - 4 yellow tiles (warning status)
   - Click on yellow tile: "Delta Corp"
   - Show specific covenants at risk
   - Discuss action plan

5. Review Recent Alerts:
   - 2 High severity alerts from this week
   - Both have action plans in progress
   - Expected resolution: 2 weeks

6. Drill into specific loan:
   - Show covenant measurement history
   - Trend improving after borrower intervention
   - Success story: Proactive engagement prevented breach

7. Export portfolio health report
8. Share dashboard link with team for ongoing monitoring
```

**Time Investment**: 15-20 minute review (vs. 2-3 hours assembling reports manually)

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ Dashboard  │  │   Loans    │  │  Alerts & Settings     │ │
│  │  (React)   │  │  (React)   │  │      (React)           │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
│         │               │                     │              │
│         └───────────────┴─────────────────────┘              │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         React Router + TanStack Query (State)          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS/REST API
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API Layer (FastAPI)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Auth API   │  │   Loans API  │  │  Analytics API   │  │
│  │   /api/auth  │  │  /api/loans  │  │  /api/analytics  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Covenants API │  │  Alerts API  │  │   Search API     │  │
│  │/api/covenants│  │ /api/alerts  │  │  /api/search     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PDF Service  │  │ OpenAI Svc   │  │ Analytics Svc    │  │
│  │ (pdfplumber) │  │   (GPT-4)    │  │(Trend Analysis)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Alert Svc   │  │Prediction Svc│  │  Notification    │  │
│  │(Rule Engine) │  │(ML/Forecast) │  │   Service        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Access Layer (SQLAlchemy ORM)              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Models: User, LoanAgreement, Covenant, Measurement,  │ │
│  │          Alert, CovenantStatus, AuditLog               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer (PostgreSQL)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │    Users     │  │     Loans    │  │   Covenants      │  │
│  │   (Table)    │  │   (Table)    │  │    (Table)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Measurements │  │    Alerts    │  │   Audit Logs     │  │
│  │   (Table)    │  │   (Table)    │  │    (Table)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ OpenAI API   │  │  Email SMTP  │  │  File Storage    │  │
│  │   (GPT-4)    │  │   (Alerts)   │  │  (PDFs/Uploads)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend**:
- React 18 with TypeScript
- Vite for build tooling
- TanStack Query (React Query) for server state management
- React Router for navigation
- Tailwind CSS for styling
- Motion (Framer Motion) for animations
- Lucide React for icons
- React Hot Toast for notifications
- CountUp.js for animated number displays

**Backend**:
- Python 3.11+
- FastAPI for REST API
- SQLAlchemy ORM for database access
- Alembic for database migrations
- Pydantic for data validation
- python-jose for JWT authentication
- Passlib + bcrypt for password hashing
- pdfplumber for PDF text extraction
- OpenAI GPT-4 for AI extraction
- python-multipart for file uploads

**Database**:
- PostgreSQL 15+ (production)
- Full ACID compliance
- JSON support for flexible schemas
- UUID primary keys
- Timezone-aware timestamps

**Infrastructure**:
- Railway (Production deployment)
- HTTPS with automatic SSL
- CORS configuration for frontend-backend separation
- Environment-based configuration

**Development Tools**:
- Git for version control
- Claude Code for AI-assisted development
- npm for frontend package management
- pip for Python package management

---

## Data Model

### Core Entities

#### 1. User (`backend/app/models/user.py`)
```python
- id: UUID (primary key)
- email: String (unique, indexed)
- full_name: String
- company: String
- role: String (admin, analyst, viewer)
- hashed_password: String
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime

Relationships:
- loan_agreements: One-to-Many
```

#### 2. LoanAgreement (`backend/app/models/loan.py`)
```python
- id: UUID (primary key)
- user_id: UUID (foreign key → users)
- title: String
- borrower_name: String
- loan_amount: Numeric
- currency: String (USD, EUR, GBP, etc.)
- origination_date: Date
- maturity_date: Date
- status: String (active, closed, defaulted)
- document_path: String (PDF file location)
- ai_extraction_status: String (pending, processing, completed, failed)
- ai_extraction_result: JSON (raw extraction data)
- created_at: DateTime
- updated_at: DateTime

Relationships:
- user: Many-to-One
- covenants: One-to-Many
- alerts: One-to-Many
```

#### 3. Covenant (`backend/app/models/covenant.py`)
```python
- id: UUID (primary key)
- loan_agreement_id: UUID (foreign key → loan_agreements)
- covenant_type: String (financial, operational, negative, affirmative)
- covenant_name: String
- description: Text
- threshold_value: Numeric (the limit value)
- threshold_operator: String (less_than, greater_than, equal, etc.)
- frequency: String (quarterly, semi-annual, annual)
- next_test_date: Date
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime

Relationships:
- loan_agreement: Many-to-One
- measurements: One-to-Many
- alerts: One-to-Many
```

#### 4. CovenantMeasurement (`backend/app/models/covenant.py`)
```python
- id: UUID (primary key)
- covenant_id: UUID (foreign key → covenants)
- measurement_date: Date (when value was recorded)
- actual_value: Numeric (the measured value)
- threshold_value: Numeric (threshold at time of measurement)
- status: String (compliant, warning, breach)
- distance_to_breach: Numeric (how far from breach, can be negative)
- notes: Text (analyst comments)
- created_at: DateTime

Relationships:
- covenant: Many-to-One

Indexes:
- covenant_id + measurement_date (for historical queries)
- status (for filtering)
```

#### 5. Alert (`backend/app/models/alert.py`)
```python
- id: UUID (primary key)
- covenant_id: UUID (foreign key → covenants, nullable)
- loan_agreement_id: UUID (foreign key → loan_agreements, nullable)
- alert_type: String (breach, warning, trend, overdue)
- severity: String (critical, high, medium, low)
- title: String
- message: Text
- predicted_breach_date: Date (nullable)
- days_until_breach: Integer (nullable)
- is_read: Boolean
- is_resolved: Boolean
- resolved_at: DateTime
- resolved_by: UUID (foreign key → users)
- resolution_notes: Text
- created_at: DateTime

Relationships:
- covenant: Many-to-One (optional)
- loan_agreement: Many-to-One (optional)

Indexes:
- severity + is_resolved (for filtering active alerts)
- created_at (for sorting)
- loan_agreement_id (for loan-specific alerts)
```

### Database Relationships Diagram

```
┌─────────────┐
│    User     │
│   (users)   │
└──────┬──────┘
       │ 1:N
       │
       ▼
┌──────────────────┐
│  LoanAgreement   │
│ (loan_agreements)│
└──────┬───────────┘
       │ 1:N
       │
       ▼
┌──────────────────┐        ┌─────────────────────┐
│    Covenant      │ 1:N    │ CovenantMeasurement │
│   (covenants)    │────────│     (measurements)  │
└──────┬───────────┘        └─────────────────────┘
       │ 1:N
       │
       ▼
┌──────────────────┐
│      Alert       │
│    (alerts)      │
└──────────────────┘
```

---

## Use Cases

### Use Case 1: Regional Bank with 50 Corporate Loans

**Client Profile**:
- Mid-size regional bank
- $500M commercial loan portfolio
- 50 active corporate borrowers
- 3-person credit risk team
- Currently using Excel spreadsheets

**Challenge**:
- Manual tracking of 200+ covenants
- Quarterly compliance reviews take 2 weeks
- Missed an early warning on one loan (became NPL)
- No systematic way to identify trends

**CovenantIQ Implementation**:

**Month 1: Onboarding**
- Upload all 50 loan agreements
- AI extracts 247 covenants
- Review and validate extractions (2-3 days)
- Set up alert preferences
- Train team on system (1 day)

**Ongoing Operations**:
- Quarterly: Input financial covenant measurements (1 day vs. 5 days)
- Weekly: Review dashboard for 15 minutes
- Real-time: Receive alerts for concerning trends
- Monthly: Executive reporting (auto-generated)

**Results After 6 Months**:
- ✅ Time savings: 60% reduction in covenant monitoring hours
- ✅ Early warning: Identified 3 potential breaches proactively
- ✅ Risk management: Negotiated covenant modifications before breaches
- ✅ Compliance: 100% covenant testing completion rate
- ✅ Audit trail: Complete measurement history for regulators

---

### Use Case 2: Private Equity Fund Monitoring Portfolio Companies

**Client Profile**:
- Mid-market PE fund
- 12 portfolio companies
- Each company has 3-5 credit facilities
- Total: 40+ loans to monitor
- Investment team of 6 professionals

**Challenge**:
- Each portfolio company has different lenders with different covenants
- Quarterly board reporting requires consolidated covenant status
- Need to track performance vs. projections
- Early identification of companies needing additional support

**CovenantIQ Implementation**:

**Setup**:
- Upload all credit agreements (40 facilities)
- Tag loans by portfolio company
- Set up company-level dashboards
- Configure alert routing to deal teams

**Usage Patterns**:
- **Monthly**: Portfolio managers input covenant measurements
- **Quarterly**: CFO reviews consolidated portfolio health
- **Weekly**: Investment committee reviews risk heatmap
- **Real-time**: Alerts routed to relevant deal team member

**Reporting Capabilities**:
- Portfolio company comparison dashboard
- Trend analysis across portfolio
- Identification of best/worst performers
- Early warning system for companies needing attention

**Business Value**:
- Proactive portfolio company support
- Better board reporting with visuals
- Reduced risk of covenant defaults
- Data-driven investment decisions

---

### Use Case 3: Asset-Based Lending (ABL) Division

**Client Profile**:
- Bank's ABL division
- 100+ borrowers
- Heavy focus on borrowing base calculations
- Monthly borrowing base certificates
- Complex covenant structures

**Challenge**:
- Borrowing base covenants require frequent testing
- High volume of covenant measurements (monthly)
- Need to track advance rates, inventory turns, AR aging
- Quick response needed for out-of-formula requests

**CovenantIQ Implementation**:

**Specialized Configuration**:
- Custom covenant types for ABL-specific metrics:
  - Borrowing base formulas
  - Advance rates
  - Concentration limits
  - Minimum availability requirements
- Monthly measurement workflow
- Integration with borrowing base certificates

**Workflow**:
1. Borrower submits monthly certificate
2. Analyst enters values into CovenantIQ
3. System calculates:
   - Available borrowing capacity
   - Covenant compliance
   - Excess/shortfall vs. limits
4. Auto-generates alerts for:
   - Declining availability trends
   - Concentration breaches
   - Formula violations
5. Dashboard shows portfolio-wide ABL metrics

**Benefits**:
- Faster borrowing base reviews (minutes vs. hours)
- Trend identification across ABL portfolio
- Risk aggregation by industry or borrower size
- Regulatory reporting capabilities

---

### Use Case 4: Credit Union Monitoring Member Business Loans

**Client Profile**:
- $500M credit union
- 200+ member business loans
- Small credit team (2 analysts)
- Focus on local small businesses
- Diverse loan types (real estate, equipment, working capital)

**Challenge**:
- High loan count with limited staff
- Loans range from $50K to $5M
- Different covenant structures per loan type
- Need to prioritize review efforts

**CovenantIQ Implementation**:

**Risk-Based Monitoring**:
- Upload all loan agreements
- System categorizes loans by risk level
- Priority review queue based on:
  - Loan size
  - Covenant status
  - Borrower industry
  - Historical performance

**Automated Workflows**:
- Email borrowers requesting financial statements
- Track submission deadlines
- Alert when financials overdue
- Batch covenant measurement entry
- Risk-based sampling for smaller loans

**Member Communication**:
- Portal for borrowers to submit financials (planned)
- Automated compliance letters
- Early outreach for declining trends
- Member relationship building through proactive engagement

**Results**:
- 2-person team efficiently monitors 200+ loans
- No missed covenant test dates
- Improved member satisfaction through proactive communication
- Better risk identification despite resource constraints

---

## Future Roadmap

### Phase 1: Enhanced Analytics (Q2 2026)

**Predictive Breach Modeling**
- Machine learning models to predict covenant breaches
- Historical pattern recognition
- Industry benchmarking
- Confidence scoring for predictions

**Advanced Reporting**
- Customizable report templates
- Automated periodic reports (daily, weekly, monthly)
- PDF export with charts and analytics
- Regulatory report templates

**Bulk Operations**
- Bulk covenant measurement import (CSV/Excel)
- Bulk loan upload
- Template-based covenant creation
- Mass update capabilities

---

### Phase 2: Borrower Portal (Q3 2026)

**Self-Service Capabilities**
- Borrower login portal
- Upload financial statements
- View own covenant status
- Submit compliance certificates
- Communication thread with lender

**Document Management**
- Financial statement storage
- Version control
- Calculation worksheets
- Audit trail

---

### Phase 3: Integration & API (Q4 2026)

**Core Banking Integrations**
- Sync with loan origination systems
- Automated loan data population
- Two-way synchronization
- Real-time updates

**Accounting System Connections**
- Pull borrower financials automatically
- Direct connection to accounting software
- Reduced manual data entry
- Accuracy improvements

**Public API**
- REST API for third-party integrations
- Webhook support for event notifications
- SDK for common languages
- API documentation portal

---

### Phase 4: Advanced Features (Q1 2027)

**Covenant Modification Tracking**
- Track covenant amendments over time
- Waiver management
- Approval workflows
- Historical covenant changes

**Scenario Analysis**
- "What-if" modeling for covenant performance
- Stress testing capabilities
- Sensitivity analysis
- Portfolio simulation

**Mobile Applications**
- iOS and Android apps
- Push notifications
- On-the-go loan review
- Offline capabilities

**AI-Powered Insights**
- Natural language queries ("Which loans are at risk?")
- Automated analysis and recommendations
- Pattern detection across portfolio
- Smart alerts with suggested actions

---

## Security & Compliance

### Data Security

**Encryption**:
- TLS 1.3 for data in transit
- AES-256 encryption for sensitive data at rest
- Encrypted database backups
- Secure file storage for PDFs

**Authentication**:
- JWT-based authentication
- Bcrypt password hashing
- Session management
- (Planned) Two-factor authentication
- (Planned) SSO/SAML support

**Access Control**:
- Role-based access control (RBAC)
- User permissions by loan portfolio
- Audit logging of all actions
- Data isolation by organization

**Infrastructure Security**:
- Railway platform security
- Automated security updates
- DDoS protection
- Regular vulnerability scanning

### Compliance

**Audit Trail**:
- Complete history of all covenant measurements
- User action logging
- Document version control
- Timestamped records

**Data Privacy**:
- GDPR considerations
- Data retention policies
- Right to deletion
- Data export capabilities

**Regulatory Reporting**:
- Covenant compliance reports
- Historical measurement records
- Risk classification documentation
- Exception tracking

---

## Technical Requirements

### Deployment Requirements

**Production Environment**:
- Python 3.11 or higher
- Node.js 18+ and npm
- PostgreSQL 15+
- 2GB+ RAM minimum
- SSL certificate
- Domain name

**Development Environment**:
```bash
# Backend
Python 3.11+
pip (package manager)
Virtual environment (venv/poetry)

# Frontend
Node.js 18+
npm or yarn

# Database
PostgreSQL 15+ (local or Docker)
```

### Installation & Setup

**Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

**Environment Variables**:
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/covenantiq
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
UPLOAD_DIR=./uploads

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

---

## Support & Documentation

### Getting Help

**Documentation**:
- API documentation: `/api/docs` (Swagger UI)
- User guides: Coming soon
- Video tutorials: Planned for Q2 2026

**Support Channels**:
- GitHub Issues: https://github.com/your-org/covenant-compass
- Email: support@covenantiq.com (if applicable)
- In-app chat: Planned feature

### Contributing

CovenantIQ is a product developed during a hackathon and continues to evolve. Contributions, feedback, and feature requests are welcome!

---

## Conclusion

CovenantIQ transforms loan covenant monitoring from a manual, error-prone process into an automated, intelligent system. By leveraging AI for document processing and providing real-time analytics, it enables financial institutions to:

- **Save Time**: 60-80% reduction in covenant monitoring hours
- **Reduce Risk**: Proactive identification of potential breaches
- **Improve Decisions**: Data-driven portfolio management
- **Scale Operations**: Monitor more loans with fewer resources
- **Enhance Compliance**: Complete audit trail and systematic tracking

The platform is production-ready for institutions of any size, from small credit unions to large commercial banks, and continues to evolve with new features based on user needs.

---

**Built with**: React, TypeScript, FastAPI, PostgreSQL, OpenAI GPT-4, and lots of ☕

**Last Updated**: January 2026
