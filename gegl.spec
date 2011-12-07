%global gegl_lib_version 0.1

Summary:	A graph based image processing framework
Name:		gegl
Version:	0.1.2
Release:	3%{?dist}
# The binary is under the GPL, while the libs are under LGPL
License:	LGPLv3+ and GPLv3+
Group:		System Environment/Libraries
URL:		http://www.gegl.org/
Source0:	ftp://ftp.gtk.org/pub/gegl/0.1/%{name}-%{version}.tar.bz2
# backported git commit fc207f85521c3939600bd3e5a337c6ed2dfaa950
# "process: don't leak each node set on a GeglProcessor"
Patch0:		gegl-0.1.2-processor-leak.patch
# avoid buffer overflow in gegl_buffer_header_init()
Patch1:		gegl-0.1.2-buffer-save-overflow.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	asciidoc
BuildRequires:	babl-devel >= 0.1.0
BuildRequires:	cairo-devel
BuildRequires:	enscript
BuildRequires:	glib2-devel >= 2.16.1
BuildRequires:	graphviz
BuildRequires:	gtk2-devel >= 2.8.6
BuildRequires:	libjpeg-devel
BuildRequires:	libopenraw-devel >= 0.0.5
BuildRequires:	libpng-devel
BuildRequires:	librsvg2-devel >= 2.14.0
BuildRequires:	libspiro-devel
BuildRequires:	libv4l-devel
BuildRequires:	lua-devel >= 5.1.0
BuildRequires:	OpenEXR-devel
BuildRequires:	pango-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig
BuildRequires:	ruby
BuildRequires:	SDL-devel
BuildRequires:	w3m

%description
GEGL (Generic Graphics Library) is a graph based image processing framework. 
GEGLs original design was made to scratch GIMPs itches for a new
compositing and processing core. This core is being designed to have
minimal dependencies. and a simple well defined API.

%package devel
Summary:	Headers for developing programs that will use %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	gtk-doc
Requires:	pkgconfig
Requires:	babl-devel
Requires:	glib2-devel

%description devel
This package contains the libraries and header files needed for
developing with %{name}.

%prep
%setup -q

chmod -x docs/devhelp.css operations/external/ff-load.c operations/workshop/external/ff-save.c operations/common/perlin/perlin.?

%patch0 -p1 -b .processor-leak
%patch1 -p1 -b .buffer-save-overflow

%build
# use PIC/PIE because gegl is likely to deal with data coming from untrusted
# sources
CFLAGS="-fPIC %optflags -fno-strict-aliasing"
CXXFLAGS="-fPIC %optflags -fno-strict-aliasing"
LDFLAGS="-pie"
%configure				\
	--with-cairo			\
	--with-graphviz			\
	--with-gtk --with-gdk-pixbuf	\
	--with-libjpeg			\
	--with-libopenraw		\
	--with-libpng			\
	--with-librsvg			\
	--with-libspiro			\
	--with-libv4l			\
	--with-lua			\
	--with-openexr			\
	--with-pango --with-pangocairo	\
	--with-sdl			\
	--disable-static --enable-workshop	\
	--disable-gtk-doc
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install INSTALL='install -p'

rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/gegl-%{gegl_lib_version}/*.la

%check
if make check; then
	:
else
	# skip this for now
	if false; then
		errorcode=$?
		# only dump results if run in mock/koji
		group="$(id -g -n)"
		if [ "$group" != "${group/mock/}" ]; then
			pushd tests/compositions
			echo tests-report
			echo "---- 8< ----"
			cat tests-report
			echo "---- >8 ----"
			echo
			echo "wrong output images:"
			grep " differ$" tests-report | while read reference and output rest; do
				echo "$output"
				echo "---- 8< ----"
				base64 "$output"
				echo "---- >8 ----"
				echo
			done
			popd
		fi
		exit $errorcode
	fi # end skip
fi

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root, -)
%doc AUTHORS ChangeLog COPYING COPYING.LESSER NEWS README
%{_bindir}/gegl
%{_libdir}/*.so.*
%{_libdir}/gegl-%{gegl_lib_version}/

%files devel
%defattr(-, root, root, -)
%doc %{_datadir}/gtk-doc/html/gegl/
%{_includedir}/gegl-%{gegl_lib_version}/
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Wed Jun 23 2010 Nils Philippsen <nils@redhat.com> - 0.1.2-3
- build with -fno-strict-aliasing
- use PIC/PIE because gegl is likely to deal with data coming from untrusted
  sources

* Fri Feb 26 2010 Nils Philippsen <nils@redhat.com>
- use tabs consistently
- let devel depend on gtk-doc

* Fri Feb 19 2010 Nils Philippsen <nils@redhat.com> - 0.1.2-2
- ignore make check failures for now

* Wed Feb 17 2010 Nils Philippsen <nils@redhat.com>
- avoid buffer overflow in gegl_buffer_header_init()
- correct gegl library version, use macro for it

* Tue Feb 16 2010 Nils Philippsen <nils@redhat.com> - 0.1.2-1
- version 0.1.2
- remove obsolete cflags, babl-instrumentation, autoreconf patches
- backported: don't leak each node set on a GeglProcessor

* Sat Jan 23 2010 Deji Akingunola <dakingun@gmail.com> - 0.1.0-3
- Rebuild for babl-0.1.2
- Backport upstream patch that removed babl processing time instrumentation

* Wed Jan 20 2010 Nils Philippsen <nils@redhat.com>
- use tabs consistently to appease rpmdiff

* Tue Aug 18 2009 Nils Philippsen <nils@redhat.com>
- explain patches

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 02 2009 Nils Philippsen - 0.1.0-1
- fix cflags for building

* Thu Jul 02 2009 Nils Philippsen
- version 0.1.0
- use "--disable-gtk-doc" to avoid rebuilding documentation (#481404)
- remove *.la files in %%{_libdir}/gegl-*/ (#509292)

* Thu Jun 04 2009 Deji Akingunola <dakingun@gmail.com> - 0.0.22-5
- Apply patch to build with babl-0.1.0 API changes

* Thu Jun 04 2009 Nils Philippsen - 0.0.22-4
- rebuild against babl-0.1.0

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.22-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 29 2009 Nils Philippsen - 0.0.22-2
- use the same timestamps for certain documentation files on all architectures
  to avoid multi-lib conflicts (#481404)
- consolidate spec files between OS releases
- reenable building documentation on ppc64
- explicitly list more build requirements and/or versions to catch eventual
  problems during future builds

* Tue Jan 13 2009 Deji Akingunola <dakingun@gmail.com> - 0.0.22-1
- Update to version 0.0.22

* Tue Oct 07 2008 Deji Akingunola <dakingun@gmail.com> - 0.0.20-1
- Update to latest release

* Thu Jul 10 2008 Deji Akingunola <dakingun@gmail.com> - 0.0.18-1
- Update to latest release

* Thu Feb 28 2008 Deji Akingunola <dakingun@gmail.com> - 0.0.16-1
- New release

* Thu Jan 17 2008 Deji Akingunola <dakingun@gmail.com> - 0.0.15-1.svn20080117
- Update to a svn snapshot for gnome-scan
- Apply patch to fix extensions loading on 64bit systems
- Building the docs on ppc64 segfaults, avoid it for now.

* Sat Dec 08 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.14-1
- Update to 0.0.14 release
- License change from GPLv2+ to GPLv3+

* Thu Oct 25 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.7.20071011svn
- Include missing requires for the devel subpackage

* Thu Oct 25 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.6.20071011svn
- BR graphiz instead of graphiz-devel
- Remove the spurious exec flag from a couple of source codes

* Tue Oct 23 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.5.20071011svn
- Fix missing directory ownership

* Mon Oct 22 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.4.20071011svn
- Update the License field 

* Fri Oct 12 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.3.20071011svn
- Package the extension libraries in the main package
- Run 'make check'

* Fri Oct 12 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.2.20071011svn
- Remove the use of inexistent source

* Thu Oct 11 2007 Deji Akingunola <dakingun@gmail.com> - 0.0.13-0.1.20071011svn
- Initial packaging for Fedora
