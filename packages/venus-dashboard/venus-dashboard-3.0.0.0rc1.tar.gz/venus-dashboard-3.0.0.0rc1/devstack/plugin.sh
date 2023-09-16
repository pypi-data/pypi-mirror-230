#!/usr/bin/env bash
# plugin.sh - DevStack plugin.sh dispatch script venus-dashboard


function install_venus_dashboard {
    setup_develop ${VENUS_DASHBOARD_DIR}
}

function configure_venus_dashboard {
    cp -a ${VENUS_DASHBOARD_DIR}/venus_dashboard/enabled/* ${HORIZON_DIR}/openstack_dashboard/local/enabled/
}

function init_venus_dashboard {
    $PYTHON ${DEST}/horizon/manage.py collectstatic --noinput
    $PYTHON ${DEST}/horizon/manage.py compress --force
}

# check for service enabled
if is_service_enabled venus-dashboard; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        # no-op
        :

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Venus Dashboard"
        install_venus_dashboard

     elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Venus Dashboard"
        configure_venus_dashboard
        init_venus_dashboard

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the venus-dashboard service
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down venus-dashboard services
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
       rm -f ${HORIZON_DIR}/openstack_dashboard/local/enabled/_40*
       rm -f ${HORIZON_DIR}/openstack_dashboard/local/enabled/_41*

       # for backward computability
       rm -f ${HORIZON_DIR}/openstack_dashboard/enabled/_40*
       rm -f ${HORIZON_DIR}/openstack_dashboard/enabled/_41*
    fi
fi
