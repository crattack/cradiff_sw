QEMU_AUDIO_DRV=none qemu-system-arm \
        -M versatilepb \
        -kernel vmlinuz-3.2.0-4-versatile \
        -initrd initrd.img-3.2.0-4-versatile \
        -hda debian_wheezy_armel_standard.qcow2 \
        -append "root=/dev/sda1" \
        -net nic \
        -net user,hostfwd=tcp::2080-:80,hostfwd=tcp::2022-:22 \
        -nographic
