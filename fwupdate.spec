%define efidir openmandriva
%define _disable_lto 1

Summary:	Tools to manage UEFI firmware updates
Name:		fwupdate
Version:	12
Release:	1
License:	GPLv2+
URL:		https://github.com/rhinstaller/fwupdate
Source0:	https://github.com/rhinstaller/fwupdate/releases/download/%{name}-%{version}/%{name}-%{version}.tar.bz2
BuildRequires:	pkgconfig(efivar) >= 0.21
BuildRequires:	pkgconfig(efiboot)
BuildRequires:	popt-devel
BuildRequires:	gnu-efi
BuildRequires:	systemd-macros
BuildRequires:	pesign
%ifarch x86_64 %{ix86}
BuildRequires:	pkgconfig(libsmbios_c)
%endif
Requires:	efibootmgr >= 0.12
ExclusiveArch:	%{x86_64} %{ix86} aarch64



%ifarch %{x86_64}
%global efiarch x64
%endif
%ifarch %{ix86}
%global efiarch ia32
%endif
%ifarch aarch64
%global efiarch aa64
%endif

%description
fwupdate provides a simple command line interface to the UEFI firmware updates.

%prep
%autosetup -p1

%build
# (tpg) clang can't build it
export CC=gcc
export CXX=g++

%make_build OPT_FLAGS="%{optflags}" CC=gcc libdir="%{_libdir}" bindir="%{_bindir}" EFIDIR="%{efidir}"

# (tpg) sign EFI image
mv -v efi/fwup%{efiarch}.efi efi/fwup%{efiarch}.unsigned.efi
%pesign -s -i efi/fwup%{efiarch}.unsigned.efi -o efi/fwup%{efiarch}.efi

%install
%make_install EFIDIR=%{efidir}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable fwupdate-cleanup.service
EOF

%files
86-%{name}.preset 
