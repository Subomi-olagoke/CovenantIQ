"""
Demo seed data script for CovenantIQ hackathon demo.
Creates 10 diverse loan agreements with realistic covenant data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from decimal import Decimal
import random

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.loan import LoanAgreement
from app.models.covenant import Covenant, CovenantMeasurement
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("🚀 CovenantIQ Demo Data Seeder")
print("="*50)

# Check if demo user already exists
existing_user = db.query(User).filter(User.email == "demo@covenantiq.io").first()
if existing_user:
    demo_user = existing_user
    print(f"✓ Using existing demo user: {demo_user.email}")
else:
    # Create demo user
    demo_user = User(
        email="demo@covenantiq.io",
        full_name="Demo User",
        company="LMA Edge Bank",
        role="analyst",
        hashed_password=pwd_context.hash("demo123")
    )
    db.add(demo_user)
    db.commit()
    print(f"✓ Created demo user: {demo_user.email} (password: demo123)")

# Demo loans with realistic data
demo_loans_data = [
    {
        "title": "Acme Manufacturing - €5M Term Loan",
        "borrower_name": "Acme Manufacturing Inc.",
        "loan_amount": 5000000,
        "currency": "EUR",
        "origination_date": date(2024, 1, 15),
        "maturity_date": date(2029, 1, 15),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Debt/EBITDA Ratio",
                "description": "Total Debt to EBITDA shall not exceed 3.5x",
                "threshold_value": 3.5,
                "threshold_operator": "less_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 2.4),
                    (date(2024, 6, 30), 2.6),
                    (date(2024, 9, 30), 2.9),
                    (date(2024, 12, 31), 3.2),  # Trending up - predict breach!
                ]
            },
            {
                "covenant_type": "financial",
                "covenant_name": "Interest Coverage Ratio",
                "description": "EBITDA to Interest Expense minimum 3.0x",
                "threshold_value": 3.0,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 4.2),
                    (date(2024, 6, 30), 3.7),
                    (date(2024, 9, 30), 3.2),
                    (date(2024, 12, 31), 3.1),  # Declining - predict breach!
                ]
            }
        ]
    },
    {
        "title": "Beta Industries - £3M Revolving Facility",
        "borrower_name": "Beta Industries Ltd",
        "loan_amount": 3000000,
        "currency": "GBP",
        "origination_date": date(2023, 6, 1),
        "maturity_date": date(2026, 6, 1),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Current Ratio",
                "description": "Current Assets to Current Liabilities minimum 1.2x",
                "threshold_value": 1.2,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 1.8),
                    (date(2024, 6, 30), 1.7),
                    (date(2024, 9, 30), 1.6),
                    (date(2024, 12, 31), 1.5),
                ]
            }
        ]
    },
    {
        "title": "Gamma Corp - $10M Senior Secured",
        "borrower_name": "Gamma Corporation",
        "loan_amount": 10000000,
        "currency": "USD",
        "origination_date": date(2023, 3, 15),
        "maturity_date": date(2028, 3, 15),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Debt Service Coverage Ratio",
                "description": "DSCR minimum 1.25x",
                "threshold_value": 1.25,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 1.45),
                    (date(2024, 6, 30), 1.50),
                    (date(2024, 9, 30), 1.55),
                    (date(2024, 12, 31), 1.60),
                ]
            }
        ]
    },
    {
        "title": "Delta Energy - €8M Project Finance",
        "borrower_name": "Delta Energy Solutions",
        "loan_amount": 8000000,
        "currency": "EUR",
        "origination_date": date(2024, 2, 1),
        "maturity_date": date(2031, 2, 1),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Debt/Equity Ratio",
                "description": "Total Debt to Total Equity maximum 2.0x",
                "threshold_value": 2.0,
                "threshold_operator": "less_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 6, 30), 1.3),
                    (date(2024, 9, 30), 1.4),
                    (date(2024, 12, 31), 1.6),
                ]
            }
        ]
    },
    {
        "title": "Epsilon Systems - $7.5M Bridge Loan",
        "borrower_name": "Epsilon Systems Inc",
        "loan_amount": 7500000,
        "currency": "USD",
        "origination_date": date(2024, 5, 20),
        "maturity_date": date(2025, 5, 20),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Quick Ratio",
                "description": "Quick Assets minimum 1.0x",
                "threshold_value": 1.0,
                "threshold_operator": "greater_or_equal",
                "frequency": "monthly",
                "measurements": [
                    (date(2024, 10, 31), 1.4),
                    (date(2024, 11, 30), 1.3),
                    (date(2024, 12, 31), 1.2),
                ]
            }
        ]
    },
    {
        "title": "Zeta Retail - £4.2M Expansion Loan",
        "borrower_name": "Zeta Retail Group",
        "loan_amount": 4200000,
        "currency": "GBP",
        "origination_date": date(2023, 9, 1),
        "maturity_date": date(2028, 9, 1),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Fixed Charge Coverage",
                "description": "FCCR minimum 1.15x",
                "threshold_value": 1.15,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 1.35),
                    (date(2024, 6, 30), 1.28),
                    (date(2024, 9, 30), 1.22),
                    (date(2024, 12, 31), 1.18),
                ]
            }
        ]
    },
    {
        "title": "Theta Logistics - €6M Working Capital",
        "borrower_name": "Theta Logistics SA",
        "loan_amount": 6000000,
        "currency": "EUR",
        "origination_date": date(2024, 3, 10),
        "maturity_date": date(2027, 3, 10),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Leverage Ratio",
                "description": "Total Debt/Total Assets maximum 0.6",
                "threshold_value": 0.6,
                "threshold_operator": "less_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 6, 30), 0.45),
                    (date(2024, 9, 30), 0.50),
                    (date(2024, 12, 31), 0.53),
                ]
            }
        ]
    },
    {
        "title": "Iota Pharma - $12M R&D Facility",
        "borrower_name": "Iota Pharmaceuticals",
        "loan_amount": 12000000,
        "currency": "USD",
        "origination_date":  date(2023, 11, 1),
        "maturity_date": date(2030, 11, 1),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Net Worth Minimum",
                "description": "Tangible Net Worth minimum $15M",
                "threshold_value": 15000000,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 18500000),
                    (date(2024, 6, 30), 17800000),
                    (date(2024, 9, 30), 16900000),
                    (date(2024, 12, 31), 16200000),
                ]
            }
        ]
    },
    {
        "title": "Kappa Technologies - £5.5M Growth Loan",
        "borrower_name": "Kappa Technologies Ltd",
        "loan_amount": 5500000,
        "currency": "GBP",
        "origination_date": date(2024, 4, 15),
        "maturity_date": date(2029, 4, 15),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Working Capital Ratio",
                "description": "Working Capital minimum £2M",
                "threshold_value": 2000000,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 6, 30), 2800000),
                    (date(2024, 9, 30), 2600000),
                    (date(2024, 12, 31), 2400000),
                ]
            }
        ]
    },
    {
        "title": "Lambda Construction - €9.2M Project Loan",
        "borrower_name": "Lambda Construction GmbH",
        "loan_amount": 9200000,
        "currency": "EUR",
        "origination_date": date(2024, 1, 10),
        "maturity_date": date(2029, 1, 10),
        "covenants": [
            {
                "covenant_type": "financial",
                "covenant_name": "Cash Flow Coverage",
                "description": "Operating Cash Flow to Debt Service minimum 1.3x",
                "threshold_value": 1.3,
                "threshold_operator": "greater_or_equal",
                "frequency": "quarterly",
                "measurements": [
                    (date(2024, 3, 31), 1.65),
                    (date(2024, 6, 30), 1.58),
                    (date(2024, 9, 30), 1.45),
                    (date(2024, 12, 31), 1.38),
                ]
            }
        ]
    }
]

print(f"\n📊 Creating {len(demo_loans_data)} demo loans...")

for idx, loan_data in enumerate(demo_loans_data, 1):
    # Create loan
    new_loan = LoanAgreement(
        user_id=demo_user.id,
        title=loan_data["title"],
        borrower_name=loan_data["borrower_name"],
        loan_amount=Decimal(str(loan_data["loan_amount"])),
        currency=loan_data["currency"],
        origination_date=loan_data["origination_date"],
        maturity_date=loan_data["maturity_date"],
        status="active",
        ai_extraction_status="completed"
    )
    db.add(new_loan)
    db.commit()
    
    print(f"\n[{idx}/{len(demo_loans_data)}] ✓ {new_loan.title}")
    
    # Create covenants
    for cov_data in loan_data["covenants"]:
        new_covenant = Covenant(
            loan_agreement_id=new_loan.id,
            covenant_type=cov_data["covenant_type"],
            covenant_name=cov_data["covenant_name"],
            description=cov_data["description"],
            threshold_value=Decimal(str(cov_data["threshold_value"])),
            threshold_operator=cov_data["threshold_operator"],
            frequency=cov_data["frequency"],
            is_active=True
        )
        db.add(new_covenant)
        db.commit()
        
        print(f"  ├─ Covenant: {new_covenant.covenant_name}")
        
        # Create measurements
        for meas_date, meas_value in cov_data["measurements"]:
            # Calculate status
            threshold = float(cov_data["threshold_value"])
            operator = cov_data["threshold_operator"]
            
            if operator == "less_or_equal":
                if meas_value <= threshold * 0.85:
                    status = "compliant"
                elif meas_value <= threshold:
                    status = "warning"
                else:
                    status = "breach"
                distance = threshold - meas_value
            elif operator == "greater_or_equal":
                if meas_value >= threshold * 1.15:
                    status = "compliant"
                elif meas_value >= threshold:
                    status = "warning"
                else:
                    status = "breach"
                distance = meas_value - threshold
            else:
                status = "compliant"
                distance = 0
            
            measurement = CovenantMeasurement(
                covenant_id=new_covenant.id,
                measurement_date=meas_date,
                actual_value=Decimal(str(meas_value)),
                threshold_value=Decimal(str(threshold)),
                status=status,
                distance_to_breach=Decimal(str(distance))
            )
            db.add(measurement)
        
        db.commit()
        print(f"  └─ {len(cov_data['measurements'])} measurements added")

print("\n" + "="*50)
print("✅ Demo data seeded successfully!")
print(f"\n📧 Login with:")
print(f"   Email: demo@covenantiq.io")
print(f"   Password: demo123")
print(f"\n📈 Created:")
print(f"   • {len(demo_loans_data)} loans")
print(f"   • Multiple covenants with historical trends")
print(f"   • Including declining trends for ML predictions!")
print("\n🚀 Ready for hackathon demo!\n")

db.close()
