import sys
import argparse
from utils.mailer import send_email_with_attachment

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    ok = send_email_with_attachment(
        recipient=args.to, subject=args.subject, body_html=args.body, attachment_path=args.file
    )
    print("OK" if ok else "FAILED")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
