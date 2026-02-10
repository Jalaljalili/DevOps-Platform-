import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "1m", target: 50 },
    { duration: "30s", target: 0 }
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300"]
  }
};

const BASE_URL = __ENV.BASE_URL;

export default function () {
  const r1 = http.get(`${BASE_URL}/healthz`);
  check(r1, { "healthz 200": (r) => r.status === 200 });

  const key = `k${__VU}-${__ITER}`;
  const r2 = http.post(`${BASE_URL}/write/${key}?value=v${__ITER}`);
  check(r2, { "write 200": (r) => r.status === 200 });

  const r3 = http.get(`${BASE_URL}/`);
  check(r3, { "root 200 or 404": (r) => r.status === 200 || r.status === 404 });

  sleep(1);
}
