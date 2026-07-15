# Serverless Industrial IoT Data Platform (AWS Suite)

A robust, enterprise-grade suite of AWS Lambda functions designed to ingest, transform, and manage high-frequency telemetry and edge AI insights from industrial IoT sensors. 

This repository showcases a modular, production-ready serverless architecture tailored for smart factory predictive maintenance platforms.


## 🔒 Security & Best Practices Demonstrated

This repository is strictly aligned with AWS security and cloud-native standards:
* **Zero Hardcoded Secrets:** All credentials, S3 bucket names, and API endpoints are decoupled from code and injected securely via **AWS Lambda Environment Variables**.
* **Zero-Dependency Footprint:** Designed around lightweight, native AWS Lambda runtime libraries to optimize performance and prevent cold-start delays.
* **Least Privilege Access:** Includes sample execution IAM policies matching strict Principle of Least Privilege (PoLP).
