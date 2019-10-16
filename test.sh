option=$1

if [ "$option" != "--only-conf" ]; then
  echo "install"
  echo "$option"
fi
if [ "$option" != "--only-install" ]; then
  echo "conf"
  echo "$option"
fi

