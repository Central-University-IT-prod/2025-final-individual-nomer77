import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from json import loads
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@pytest.mark.django_db
class TestFromClientToStat(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.exist_client_id = "99804214-3cdc-4941-933a-dfaf3e273712"

    def setup_data(self):
        advertiser_payloads = loads(open(os.path.join(BASE_DIR, "payloads/advertisers.json")).read())
        campaign_payloads = loads(open(os.path.join(BASE_DIR, "payloads/campaigns.json")).read())
        client_payloads = loads(open(os.path.join(BASE_DIR, "payloads/bulk_clients.json")).read())
        ml_score_payloads = loads(open(os.path.join(BASE_DIR, "payloads/ml_scores.json")).read())

        response = self.client.post("/advertisers/bulk", data=advertiser_payloads, format='json')
        assert response.status_code == 201

        response = self.client.post("/clients/bulk", data=client_payloads, format='json')
        assert response.status_code == 201

        for campaign in campaign_payloads:
            response = self.client.post(
                f"/advertisers/{campaign['advertiser_id']}/campaigns",
                data=campaign["campaign_data"],
                format='json'
            )
            assert response.status_code == 201

        for ml in ml_score_payloads:
            response = self.client.post("/ml-scores", data=ml, format='json')
            assert response.status_code == 200


    def test_total_campaign_stats(self):
        self.client.post("/time/advance", data={"current_date": 0})

        self.setup_data()

        self.client.post("/time/advance", data={"current_date": 7})

        response = self.client.get(f"/ads?client_id={self.exist_client_id}")
        print(response)
        assert response.status_code == 200

        data = response.json()
        assert "ad_id" in data
        campaign_id = data["ad_id"]

        response = self.client.get(f"/stats/campaigns/{campaign_id}")
        assert response.status_code == 200

        data = response.json()
        assert data == {
            "impressions_count": 1,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 1000.10,
            "spent_clicks": 0,
            "spent_total": 1000.10
        }

        response = self.client.post(f"/ads/{campaign_id}/click", data={"client_id": self.exist_client_id})
        assert response.status_code == 204

        response = self.client.get(f"/stats/campaigns/{campaign_id}")
        assert response.status_code == 200

        data = response.json()

        assert data == {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100,
            "spent_impressions": 1000.10,
            "spent_clicks": 2000.90,
            "spent_total": 3001.0,
        }


    def test_get_total_stats_by_advertiser(self):
        self.client.post("/time/advance", data={"current_date": 0})

        self.setup_data()

        self.client.post("/time/advance", data={"current_date": 7})

        for i in range(2):
            response = self.client.get(f"/ads?client_id={self.exist_client_id}")
            assert response.status_code == 200

            data = response.json()
            assert "ad_id" in data
            campaign_id = data["ad_id"]

            response = self.client.post(f"/ads/{campaign_id}/click", data={"client_id": self.exist_client_id})
            assert response.status_code == 204

        advertiser_id = "e04d35cd-e24b-4bfd-b5fa-6ac1c12ae8a0"
        response = self.client.get(f"/stats/advertisers/{advertiser_id}/campaigns")
        assert response.status_code == 200

        assert response.json() == {
            "impressions_count": 2,
            "clicks_count": 2,
            "conversion": 100,
            "spent_impressions": 1000.10 + 160.0,
            "spent_clicks": 2000.90 + 240.0,
            "spent_total": 3001.0 + 400.0
        }