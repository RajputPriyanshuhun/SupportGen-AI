import os

def validate_project_structure():
    print("🔍 [SupportGen-AI] Validating project structure and dataset integrity...\n")
    
    # Required directories and files check
    required_dirs = ['data', 'kb', 'src', 'app', 'tools']
    required_files = [
        'data/customers.csv',
        'data/orders.csv',
        'data/order_items.csv',
        'data/support_logs.csv',
        'data/products.csv',
        'data/pincodes.csv',
        'data/holidays.csv',
        'kb/pol_returns_v4.md',
        'kb/pol_refunds.md',
        'kb/pol_cancellations.md',
        'kb/help_track_order.md',
        'kb/faq_general.md'
    ]
    
    missing_items = []
    
    # Check directories
    for d in required_dirs:
        if os.path.exists(d) and os.path.isdir(d):
            print(f"📁 Directory found: {d}/")
        else:
            print(f"❌ Missing directory: {d}/")
            missing_items.append(d)
            
    print("\n-------------------------------------------\n")
    
    # Check files
    for f in required_files:
        if os.path.exists(f) and os.path.isfile(f):
            print(f"✅ File found: {f}")
        else:
            print(f"⚠️ Warning/Missing file: {f}")
            missing_items.append(f)
            
    print("\n-------------------------------------------\n")
    if len(missing_items) == 0:
        print("🎉 SUCCESS: All required dataset files and directories are verified successfully!")
    else:
        print(f"⚠️ Total missing items detected: {len(missing_items)}. Please check your folder structure.")

if __name__ == "__main__":
    validate_project_structure()