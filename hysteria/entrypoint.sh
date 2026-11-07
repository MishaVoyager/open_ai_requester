#!/bin/sh
set -eu

for name in HYSTERIA_MIA_PASSWORD HYSTERIA_NOSKOVS_PASSWORD HYSTERIA_HIPSTERS_PASSWORD HYSTERIA_OTHERS_PASSWORD; do
    eval "value=\${$name:-}"
    case "$value" in
        ""|*[!A-Za-z0-9_-]*)
            echo "$name must contain only A-Z, a-z, 0-9, _ or -" >&2
            exit 1
            ;;
    esac
done

umask 077
mkdir -p /run/hysteria
cat > /run/hysteria/config.yaml <<EOF
listen: 0.0.0.0:443

tls:
  cert: /etc/letsencrypt/live/mishavoyager.fyi/fullchain.pem
  key: /etc/letsencrypt/live/mishavoyager.fyi/privkey.pem
  sniGuard: strict

auth:
  type: userpass
  userpass:
    mia: ${HYSTERIA_MIA_PASSWORD}
    noskovs: ${HYSTERIA_NOSKOVS_PASSWORD}
    hipsters: ${HYSTERIA_HIPSTERS_PASSWORD}
    others: ${HYSTERIA_OTHERS_PASSWORD}

ignoreClientBandwidth: true
congestion:
  type: bbr
  bbrProfile: standard

masquerade:
  type: proxy
  proxy:
    url: http://127.0.0.1:7999
    rewriteHost: false
    insecure: false
    xForwarded: false

acl:
  inline:
    - reject(0.0.0.0/8)
    - reject(10.0.0.0/8)
    - reject(100.64.0.0/10)
    - reject(127.0.0.0/8)
    - reject(169.254.0.0/16)
    - reject(172.16.0.0/12)
    - reject(192.168.0.0/16)
    - reject(224.0.0.0/4)
    - reject(::1/128)
    - reject(fc00::/7)
    - reject(fe80::/10)
    - reject(ff00::/8)
    - direct(all)
EOF

exec hysteria "$@"
