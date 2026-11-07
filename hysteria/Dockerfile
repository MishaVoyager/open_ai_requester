FROM tobyxdd/hysteria:v2.13.0@sha256:92b06917b2abb940e90ea6dc9215c1b1ceea69fa7edc1374daf3cde36e422740

COPY entrypoint.sh /usr/local/bin/voyager-hysteria-entrypoint
RUN chmod 0755 /usr/local/bin/voyager-hysteria-entrypoint

ENTRYPOINT ["/usr/local/bin/voyager-hysteria-entrypoint"]
CMD ["server", "-c", "/run/hysteria/config.yaml"]
