"""
API测试脚本
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:5001"
TEST_CHAT_ID = os.getenv('CHAT_ID')


def test_health_check():
    """测试健康检查"""
    print("\n=== Test Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_send_message():
    """测试发送消息"""
    print("\n=== Test Send Message ===")
    data = {
        "message": "🔔 **API Test Message**\n\nThis is a test message"
    }
    response = requests.post(f"{BASE_URL}/api/v1/send", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_send_formatted():
    """测试发送格式化消息"""
    print("\n=== Test Send Formatted Message ===")
    data = {
        "chain": "Ethereum",
        "token": "USDT",
        "amount": 10000,
        "action": "Buy",
        "from_address": "0x1234567890",
        "to_address": "0xabcdefabcd",
        "tx_hash": "0xdeadbeef"
    }
    response = requests.post(f"{BASE_URL}/api/v1/send/formatted", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


if __name__ == '__main__':
    print("=" * 60)
    print("  Telegram Signal API - Test Suite")
    print("=" * 60)

    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Send Message", test_send_message()))
    results.append(("Send Formatted", test_send_formatted()))

    print("\n" + "=" * 60)
    print("  Test Results")
    print("=" * 60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")

    passed = sum(1 for _, r in results if r)
    print(f"\n  Total: {passed}/{len(results)} passed")
    print("=" * 60)
