import http from 'k6/http';
import { check } from 'k6';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';
import { SharedArray } from 'k6/data';

// Load CSV once before test starts
const csvData = new SharedArray('notifications', function () {
  const data = papaparse.parse(open('./notifications.csv'), {
    header: true,
  }).data;
  return data;
});

export let options = {
  vus: 10, // 10 virtual users
  iterations: 100, // total 100 requests
};

export default function () {
  // Pick a row based on iteration number
  const row = csvData[__ITER % csvData.length];

  const payload = JSON.stringify({
    notification_type: row.notification_type,
    template_code: row.template_code,
    variables: { name: row.name, link: row.link },
    request_id: row.request_id,
    priority: Number(row.priority),
  });

  const headers = {
    'Content-Type': 'application/json',
    Authorization: 'Bearer <your_jwt_token>',
  };

  let res = http.post('http://localhost:8080/api/v1/notifications/', payload, {
    headers,
  });

  check(res, {
    'status is 201': (r) => r.status === 201,
  });
}
