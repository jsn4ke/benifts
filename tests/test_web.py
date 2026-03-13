"""Web 应用测试"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


class TestWebApp:
    """Web 应用测试"""

    @pytest.fixture
    def client(self):
        """Flask 测试客户端"""
        with patch('src.web.app.analyzer'), \
             patch('src.web.app.FileStorage'), \
             patch('src.web.app.CMBScraper'):
            from src.web.app import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_index_page(self, client):
        """测试首页加载"""
        with patch('src.web.app.FileStorage') as mock_storage:
            mock_storage.return_value.load_csv.return_value = []
            mock_storage.return_value.load_json.return_value = []

            response = client.get('/')
            assert response.status_code == 200
            data = response.data.decode('utf-8')
            assert 'B2 - 理财产品数据平台' in data
            assert '产品列表' in data

    def test_products_api_no_data(self, client):
        """测试 API - 无数据"""
        with patch('src.web.app.FileStorage') as mock_storage:
            mock_storage.return_value.load_csv.side_effect = FileNotFoundError()
            mock_storage.return_value.load_json.side_effect = FileNotFoundError()

            response = client.get('/api/products')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data

    def test_products_api_with_data(self, client):
        """测试 API - 有数据"""
        from src.models.product import Product
        from datetime import datetime

        mock_products = [
            Product(name="Test 1", code="T001", bank="Test Bank", net_value=1.05),
            Product(name="Test 2", code="T002", bank="Test Bank", net_value=1.10),
        ]

        with patch('src.web.app.FileStorage') as mock_storage:
            mock_storage.return_value.load_csv.return_value = mock_products

            response = client.get('/api/products')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['total'] == 2
            assert len(data['products']) == 2

    def test_products_api_with_filters(self, client):
        """测试 API - 带筛选条件"""
        from src.models.product import Product

        mock_products = [
            Product(name="Bank A 1", code="A001", bank="Bank A", net_value=1.05),
            Product(name="Bank B 1", code="B001", bank="Bank B", net_value=1.10),
        ]

        with patch('src.web.app.FileStorage') as mock_storage:
            mock_storage.return_value.load_csv.return_value = mock_products

            # 按银行筛选
            response = client.get('/api/products?bank=Bank+A')
            data = response.get_json()
            assert data['total'] == 1
            assert data['products'][0]['bank'] == 'Bank A'

            # 按净值筛选
            response = client.get('/api/products?min_net_value=1.07')
            data = response.get_json()
            assert data['total'] == 1
            assert data['products'][0]['net_value'] == 1.10

    def test_bonus_report_page(self, client):
        """测试红利期报告页面"""
        with patch('src.web.app.FileStorage') as mock_storage:
            mock_storage.return_value.load_csv.return_value = []

            response = client.get('/bonus-report')
            assert response.status_code == 200
            data = response.data.decode('utf-8')
            assert '红利期分析报告' in data

    def test_analysis_api(self, client):
        """测试分析 API"""
        from src.models.product import Product

        mock_products = [
            Product(name="Test 1", code="T001", bank="Test Bank", net_value=1.05),
        ]

        with patch('src.web.app.FileStorage') as mock_storage, \
             patch('src.web.app.analyzer') as mock_analyzer:
            mock_storage.return_value.load_csv.return_value = mock_products
            mock_analyzer.analyze_net_value_changes.return_value = []
            mock_analyzer.find_high_growth_products.return_value = []
            mock_analyzer.identify_bonus_periods.return_value = []

            response = client.get('/api/analysis')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'total_changes' in data
            assert 'total_bonus_periods' in data

    def test_refresh_api(self, client):
        """测试刷新数据 API"""
        from src.models.product import Product

        with patch('src.web.app.CMBScraper') as mock_scraper, \
             patch('src.web.app.FileStorage') as mock_storage, \
             patch('src.web.app.analyzer') as mock_analyzer:
            # Mock 爬虫 - 返回一些数据而非空列表
            mock_products = [
                Product(name="Test 1", code="T001", bank="Test Bank", net_value=1.05),
                Product(name="Test 2", code="T002", bank="Test Bank", net_value=1.10),
            ]
            mock_scraper.return_value.fetch_products.return_value = [Mock(name="P1")]  # 返回一些原始数据
            mock_scraper.return_value.to_product_list.return_value = mock_products
            mock_storage.return_value.save_csv.return_value = Mock()
            mock_storage.return_value.save_json.return_value = Mock()

            response = client.get('/api/refresh')
            data = response.get_json()
            assert data['success'] is True


class TestFileStorageLoadMethods:
    """FileStorage 加载方法测试"""

    def test_load_csv_not_found(self):
        """测试加载不存在的 CSV 文件"""
        from src.storage.file_storage import FileStorage
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        storage = FileStorage(temp_dir)

        products = storage.load_csv('nonexistent.csv')
        assert len(products) == 0

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_json_not_found(self):
        """测试加载不存在的 JSON 文件"""
        from src.storage.file_storage import FileStorage
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        storage = FileStorage(temp_dir)

        products = storage.load_json('nonexistent.json')
        assert len(products) == 0

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_csv_valid(self):
        """测试加载有效的 CSV 文件"""
        from src.storage.file_storage import FileStorage
        from src.models.product import Product
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        storage = FileStorage(temp_dir)

        # 保存一些产品
        products = [
            Product(name="Test 1", code="T001", bank="Test Bank", net_value=1.05),
            Product(name="Test 2", code="T002", bank="Test Bank", net_value=1.10),
        ]
        storage.save_csv(products, 'test.csv')

        # 加载回来
        loaded = storage.load_csv('test.csv')
        assert len(loaded) == 2
        assert loaded[0].name == "Test 1"
        assert loaded[0].net_value == 1.05

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_json_valid(self):
        """测试加载有效的 JSON 文件"""
        from src.storage.file_storage import FileStorage
        from src.models.product import Product
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        storage = FileStorage(temp_dir)

        # 保存一些产品
        products = [
            Product(name="Test 1", code="T001", bank="Test Bank", net_value=1.05),
            Product(name="Test 2", code="T002", bank="Test Bank", net_value=1.10),
        ]
        storage.save_json(products, 'test.json')

        # 加载回来
        loaded = storage.load_json('test.json')
        assert len(loaded) == 2
        assert loaded[0].name == "Test 1"
        assert loaded[0].net_value == 1.05

        shutil.rmtree(temp_dir, ignore_errors=True)
