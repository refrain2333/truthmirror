#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("检查依赖包...")

try:
    import requests
    print("✅ requests 可用")
except ImportError:
    print("❌ requests 不可用")

try:
    from bs4 import BeautifulSoup
    print("✅ beautifulsoup4 可用")
except ImportError:
    print("❌ beautifulsoup4 不可用")

try:
    import lxml
    print("✅ lxml 可用")
except ImportError:
    print("❌ lxml 不可用")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv 可用")
except ImportError:
    print("❌ python-dotenv 不可用")

print("检查完成")
