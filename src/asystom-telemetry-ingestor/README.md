# Serverless Industrial IoT Data Ingestor (AWS Lambda & S3)

A production-grade AWS Lambda solution written in Python to dynamically ingest high-frequency telemetry and predictive maintenance AI insights from Asystom IoT beacons, storing the output as organized JSON payloads in Amazon S3. 

This project demonstrates clean serverless architecture patterns, cloud security best practices (avoiding hardcoded credentials), and dynamic API data fetching over a rolling 30-day historical time frame.

## 🚀 Key Features

* **Dual-Endpoint Integration:** Dynamically fetches both raw physical baseline telemetry (`Signature`) and edge-calculated AI anomalies (`Signature_Anomaly`).
* **Dynamic Parameterization:** Accepts individual `device_mac` parameters via Lambda events, or can be scaled to fetch an entire fleet configuration list from an S3 JSON registry.
* **Rolling Time-Window Queries:** Calculates and requests exact millisecond-precision timestamps spanning a sliding **30-day lookback window** (Today minus 30 Days) rather than a static row count limit.
* **Zero-Dependency Core:** Written strictly using Python's built-in `urllib3` and standard libraries. It does not require packaging heavy external libraries (like `requests` or `PyYAML`), keeping cold-starts to a minimum on AWS Lambda.
* **S3 Integration with Organized Key Paths:** Automatically uploads distinct JSON payloads with chronological timestamps directly into a target S3 bucket bucket under partitioned paths.

---

## 🛠️ System Architecture

1. **Trigger:** The Lambda function is triggered manually, via AWS EventBridge (cron-job scheduler), or downstream workflows passing a payload.
2. **Compute:** AWS Lambda runs the Python script, calculating the exact millisecond Unix epoch start/end boundaries for the 30-day window.
3. **API Call:** Lambda authenticates using Basic Auth headers and securely queries the external Asystom API.
4. **Storage:** Standard outputs are captured, pretty-printed, and written to S3 with standardized, searchable file names:
   * `s3://[your-bucket]/asystom-api-data/signature_[device_mac]_[timestamp].json`
   * `s3://[your-bucket]/asystom-api-data/signature_anomaly_[device_mac]_[timestamp].json`

---

## 📁 Repository Contents

* `src/lambda_function.py`: The core Lambda handler processing the API logic, dynamic date generations, and S3 uploads.
* `config/devices.json`: A template demonstrating how you can extend the script to dynamically loop through an entire industrial plant's list of assets.

---

## ⚙️ How to Deploy & Test

### Prerequisites
* An AWS Account with access to AWS Lambda and IAM.
* An S3 bucket (e.g., `glb-core-agenticai-input`).
* Asystom API credentials (Username/Password).

### Lambda IAM Execution Role Permissions
Ensure your Lambda's IAM execution role has permissions to write to your target S3 bucket. At a minimum, it requires:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
