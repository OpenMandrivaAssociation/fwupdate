%define efidir openmandriva
%define _disable_lto 1

Summary:	Tools to manage UEFI firmware updates
Name:		fwupdate
Version:	0.5
Release:	1
License:	GPLv2+
URL:		https://github.com/rhinstaller/fwupdate
Source0:        https://github.com/rhinstaller/fwupdate/releases/download/%{name}-%{version}/%{name}-%{version}.tar.bz2
BuildRequires:	pkgconfig(efivar) >= 0.21
BuildRequires:	popt-devel
BuildRequires:	gnu-efi
BuildRequires:	systemd
Requires:	efibootmgr >= 0.12
ExclusiveArch:	x86_64 %{ix86} aarch64

%description
fwupdate provides a simple command line interface to the UEFI firmware updates.

%prep
%setup -q

%build
# (tpg) fix build with clang
%global optflags %optflags -Qunused-arguments

%setup_compile_flags

%make CC=%{__cc} libdir="%{_libdir}" bindir="%{_bindir}" EFIDIR="%{efidir}"

%install
%makeinstall_std EFIDIR=%{efidir}

%files
%dir /boot/efi/EFI/%{efidir}/fw/
%{_bindir}/fwupdate
/boot/efi/EFI/%{efidir}/fwupdate.efi
%{_datadir}/locale/en/*.po
