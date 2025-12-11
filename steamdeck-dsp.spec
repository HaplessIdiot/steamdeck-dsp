Name:           steamdeck-dsp
Version:        0.61
Release:        1
Summary:        Steam Deck Audio Processing
License:        GPL-2.0
URL:            https://gitlab.com/evlaV/valve-hardware-audio-processing
Source0:        valve-hardware-audio-processing-%{version}.tar.xz
Patch0:         rpm.patch
Patch1:         confdir.patch

# Runtime deps on OpenMandriva
Requires:       wireplumber
Requires:       lib64rnnoise0
Requires:       pipewire
Requires:       ladspa-devel

# Build deps adjusted for OpenMandriva naming
BuildRequires:  wireplumber
BuildRequires:  make
BuildRequires:  faust
BuildRequires:  faust-tools
BuildRequires:  boost-devel
BuildRequires:  lv2-devel
BuildRequires:  gcc-c++
BuildRequires:  ladspa-devel
BuildRequires:  lib64rnnoise-devel
BuildRequires:  lib64pipewire-devel
BuildRequires:  xz
BuildRequires:  pkgconfig(systemd)

Provides:       valve-hardware-audio-processing = %{version}
ExclusiveArch:  x86_64

%description
This package contains all audio configurations and DSP processing
used by SteamOS on the Steam Deck.

%prep
%autosetup -p0 -p1 -n valve-hardware-audio-processing-%{version}

%build
%make_build FAUSTINC="/usr/include/faust" FAUSTLIB="/usr/share/faust"

%install
%make_install DEST_DIR="%{buildroot}" LIB_DIR="%{buildroot}%{_libdir}"
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}/
cp LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE

# Compress firmware blobs
xz --check=crc32 %{buildroot}%{_prefix}/lib/firmware/amd/sof/*
xz --check=crc32 %{buildroot}%{_prefix}/lib/firmware/amd/sof-tplg/*

# Move configs into hwsupport
mkdir -p %{buildroot}%{_libexecdir}/hwsupport
mv %{buildroot}%{_datadir}/wireplumber/hardware-profiles/wireplumber-hwconfig \
   %{buildroot}%{_libexecdir}/hwsupport/wireplumber-hwconfig
mv %{buildroot}%{_datadir}/pipewire/hardware-profiles/pipewire-hwconfig \
   %{buildroot}%{_libexecdir}/hwsupport/pipewire-hwconfig

# Clean up defaults
rm -fr %{buildroot}%{_datadir}/wireplumber/hardware-profiles/default
rm -fr %{buildroot}%{_datadir}/pipewire/hardware-profiles/default

%pre
%systemd_pre pipewire-sysconf.service wireplumber-sysconf.service

%post
%systemd_post pipewire-sysconf.service wireplumber-sysconf.service

%preun
%systemd_preun pipewire-sysconf.service wireplumber-sysconf.service

%postun
%systemd_postun_with_restart wireplumber-sysconf.service pipewire-sysconf.service

%files
%license LICENSE
%dir %{_prefix}/lib/firmware/amd
%{_prefix}/lib/firmware/amd/*
%dir %{_libexecdir}/hwsupport
%{_libexecdir}/hwsupport/wireplumber-hwconfig
%{_libexecdir}/hwsupport/pipewire-hwconfig
%{_libdir}/lv2/valve_*
%dir %{_datadir}/alsa/ucm2
%{_datadir}/alsa/ucm2/conf.d/acp5x/*.conf
%{_datadir}/alsa/ucm2/conf.d/sof-nau8821-max/*.conf
%{_datadir}/wireplumber/hardware-profiles/*
%{_unitdir}/wireplumber-sysconf.service
%{_datadir}/pipewire/hardware-profiles/*
%{_unitdir}/pipewire-sysconf.service

%changelog
* Thu Dec 11 2025 Ported for OpenMandriva by Collin Beyer <legendarydood@gmail.com>
- Adjusted BuildRequires to match OpenMandriva package names
- Removed openSUSE-specific pipewire-modules-0_3 and ladspa-rnnoise
- Verified faust headers bundled in faust package
