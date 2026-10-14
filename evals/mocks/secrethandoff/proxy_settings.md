Put these variables in front of one command only, never in your shell profile or the client's environment:
HTTPS_PROXY=http://sh:mockcredential@127.0.0.1:50000 SSL_CERT_FILE=/tmp/mock/ca.pem CURL_CA_BUNDLE=/tmp/mock/ca.pem NODE_EXTRA_CA_CERTS=/tmp/mock/ca.pem REQUESTS_CA_BUNDLE=/tmp/mock/ca.pem

The proxy serves only the hosts in the ready secrets' policies.
