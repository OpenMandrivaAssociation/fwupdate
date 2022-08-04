# Debuginfo generator chokes on UEFI executables, but
# the package has its own way to generate debuginfo
%define debug_package %{nil}
%define __debug_install_post %{nil}

%define efidir openmandriva

Summary:	Tools to manage UEFI firmware updates
Name:		fwupdate
Version:	12
Release:	4
License:	GPLv2+
Group:	System/Boot and Init
URL:		https://github.com/rhinstaller/fwupdate
Source0:	https://github.com/rhinstaller/fwupdate/releases/download/%{name}-%{version}/%{name}-%{version}.tar.bz2
# From upstream security branch
Patch0:		0001-efi-Fix-build-on-armhf.patch
Patch1:		0002-Update-README-to-show-the-merge-into-fwupd-Closes-7.patch
Patch2:		0003-libfwup-shouldn-t-create-ux-capsule-when-getting-ux-.patch
Patch3:		0004-Correct-typo.patch
Patch4:		0005-efi-elf_aarch64_efi.lds-Sync-up-with-gnu-efi.patch
# OMV additions
Patch10:	fwupdate-libefivar-38.patch
BuildRequires:	pkgconfig(efivar) >= 0.21
BuildRequires:	pkgconfig(efiboot)
BuildRequires:	popt-devel
BuildRequires:	gnu-efi
BuildRequires:	systemd-macros
BuildRequires:	pesign
%ifarch %{x86_64} %{ix86}
BuildRequires:	pkgconfig(libsmbios_c)
%endif
Requires:	efibootmgr >= 0.12
ExclusiveArch:	%{x86_64} %{ix86} %{aarch64}

%libpackage fwup 1
%define libname %mklibname fwup 1
%define devel %mklibname fwup -d

%ifarch %{x86_64}
%global efiarch x64
%endif
%ifarch %{ix86}
%global efiarch ia32
%endif
%ifarch %{aarch64}
%global efiarch aa64
%endif

%description
fwupdate provides a simple command line interface to the UEFI firmware updates.

%package -n %{devel}
Summary: Development files for the UEFI firmware update library
Group: Development/C and C++
Requires: %{libname} = %{EVRD}

%description -n %{devel}
Development files for the UEFI firmware update library

%package debug
Summary: Debug symbols for %{name}
Requires: %{libname} = %{EVRD}

%description debug
Debug symbols for %{name}

%prep
%autosetup -p1

%build
# (tpg) clang can't build it
export CC=gcc
export CXX=g++

# Fix build with gcc 12
sed -i -e 's,-Werror ,-Werror -Wno-error=address-of-packed-member -Wno-error=pointer-sign ,' linux/Makefile efi/Makefile
%make_build CC=gcc libdir="%{_libdir}" bindir="%{_bindir}" EFIDIR="%{efidir}"

# (tpg) sign EFI image
mv -v efi/fwup%{efiarch}.efi efi/fwup%{efiarch}.unsigned.efi
%pesign -s -i efi/fwup%{efiarch}.unsigned.efi -o efi/fwup%{efiarch}.efi

%install
%make_install EFIDIR=%{efidir}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable fwupdate-cleanup.service
EOF

%if "%{_unitdir}" != "%{_prefix}/lib/systemd/system"
mkdir -p %{buildroot}%{_unitdir}
mv %{buildroot}%{_prefix}/lib/systemd/system/*.service %{buildroot}%{_unitdir}
rm -rf %{buildroot}%{_prefix}/lib/systemd
%endif

# Bogus
rm -rf %{buildroot}%{_datadir}/locale/en

%files
%{_unitdir}/fwupdate-cleanup.service
%{_presetdir}/86-%{name}.preset
/boot/efi/EFI/%{efidir}/fwup*.efi
%{_bindir}/fwupdate
%{_libexecdir}/fwupdate
%{_datadir}/bash-completion/completions/fwupdate
%{_mandir}/man1/*

%files -n %{devel}
%{_includedir}/*.h
%{_libdir}/libfwup.so
%{_libdir}/pkgconfig/fwup.pc
%{_mandir}/man3/*

%files debug
%{_prefix}/lib/debug/.build-id/*
%{_prefix}/src/debug/*
%{_prefix}/lib/debug/boot/efi/EFI/*/*.debug
