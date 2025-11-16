#!/bin/bash
# Determine protonvpn port via gluetun and update qbittorrent
#
# Add the following to sudo crontab -e to run every 5 minutes
# */5 * * * * /bin/sh /path/to/update_qbit_port.sh
# For synology users, run the script as root via the task scheduler every 5 minutes.

QBITTORRENT_PORT=
QBITTORRENT_SERVER=          # usually localhost if running all containers on the same machine
QBITTORRENT_USER=            # qbittorrent username
QBITTORRENT_PASS=            # qbittorrent password

GLUETUN_SERVER=              # usually localhost if running all containers on the same machine
GLUETUN_PORT=                # API server
GLUETUN_AUTH_USER=           # API auth username
GLUETUN_AUTH_PASS=           # API auth password

VPN_CT_NAME=                 # Gluetun container name

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

findconfiguredport() {
    curl -s -i --header "Referer: http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}" --cookie "$1" "http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}/api/v2/app/preferences" | grep -oP '(?<=\"listen_port\"\:)(\d{1,5})'
}

findactiveport() {
    curl -u ${GLUETUN_AUTH_USER}:${GLUETUN_AUTH_PASS} -s -i "http://${GLUETUN_SERVER}:${GLUETUN_PORT}/v1/portforward" | grep -oP '(?<=\"port\"\:)(\d{1,5})'
}

getpublicip() {
    curl -u ${GLUETUN_AUTH_USER}:${GLUETUN_AUTH_PASS} -s -i "http://${GLUETUN_SERVER}:${GLUETUN_PORT}/v1/publicip/ip" | grep -oP '(?<="public_ip":.)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
}

qbt_login() {
    qbt_sid=$(curl -s -i --header "Referer: http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}" --data "username=${QBITTORRENT_USER}" --data-urlencode "password=${QBITTORRENT_PASS}" "http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}/api/v2/auth/login" | grep -oP '(?!set-cookie:.)SID=.*(?=\;.HttpOnly\;)')
    return $?
}

qbt_changeport() {
    curl -s -i --header "Referer: http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}" --cookie "$1" --data-urlencode "json={\"listen_port\":$2,\"random_port\":false,\"upnp\":false}" "http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}/api/v2/app/setPreferences" >/dev/null 2>&1
    return $?
}

qbt_checksid() {
    if curl -s --header "Referer: http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}" --cookie "${qbt_sid}" "http://${QBITTORRENT_SERVER}:${QBITTORRENT_PORT}/api/v2/app/version" | grep -qi forbidden; then
        return 1
    else
        return 0
    fi
}

qbt_isreachable() {
    nc -4 -vw 5 ${QBITTORRENT_SERVER} ${QBITTORRENT_PORT} &>/dev/null 2>&1
}

check_vpn_ct_health() {
    while true;
    do
        if ! docker inspect "${VPN_CT_NAME}" --format='{{json .State.Health.Status}}' | grep -q '"healthy"'; then
            echo "$(timestamp) | Waiting for ${VPN_CT_NAME} healthy state.."
            sleep 3
        else
            echo "$(timestamp) | VPN container ${VPN_CT_NAME} in healthy state!"
            break
        fi
    done
}

get_portmap() {
    res=0

    # Get Public IP
    public_ip=$(getpublicip)
    if [ -z "$public_ip" ]; then
      echo "$(timestamp) | Error: Unable to get public IP from Gluetun"
      echo "$(timestamp) | Attempted ip: ${GLUETUN_SERVER}. Port ${GLUETUN_PORT}"
      exit 1
    fi

    echo "$(timestamp) | Public IP: ${public_ip}"

    if ! qbt_checksid; then
        echo "$(timestamp) | qBittorrent Cookie invalid, getting new SessionID"
        if qbt_login; then
            echo "$(timestamp) | Got new SessionID"
        else
            echo "$(timestamp) | Failed getting new SessionID from qBittorrent"
            return 1
        fi
    else
        echo "$(timestamp) | qBittorrent SessionID Ok!"
    fi

    # Get configured port
    configured_port=$(findconfiguredport "${qbt_sid}")
    if [ -z "$configured_port" ]; then
      echo "Error: Unable to get configured_port"
      exit 1
    fi
    echo "$(timestamp) | Configured Port: ${configured_port}"

    # Get active port
    active_port=$(findactiveport)
    if [ -z "$active_port" ]; then
      echo "Error: Unable to get active port"
      exit 1
    fi
    echo "$(timestamp) | Active Port: ${active_port}"

    # Deal with current configuration
    if [ ${configured_port} != ${active_port} ]; then
        if qbt_changeport "${qbt_sid}" ${active_port}; then
            echo "$(timestamp) | Port Changed to: $(findconfiguredport ${qbt_sid})"
        else
            echo "$(timestamp) | Port Change failed."
            res=1
        fi
    else
        echo "$(timestamp) | Port OK (Act: ${active_port} Cfg: ${configured_port})"
    fi

    return $res
}

public_ip=
configured_port=
active_port=
qbt_sid=

# Wait for a healthy state on the VPN container
check_vpn_ct_health

# check and possibly update the port
get_portmap

exit $?
