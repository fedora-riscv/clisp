%global commit 90b363151ce0f8a7ffd301028f92ec865807276a
%global shortcommit %(c=%{commit}; echo ${c:0:7})

# There is a plus on the end for unreleased versions, not for released versions
%global instdir %{name}-%{version}+

Name:		clisp
Summary:	ANSI Common Lisp implementation
Version:	2.49.93
Release:	3.%{shortcommit}git%{?dist}
License:	GPLv2+
URL:		http://www.clisp.org/
# The source for this package was pulled from upstream's git repository.
Source0:	https://gitlab.com/gnu-clisp/%{name}/repository/archive.tar.gz?ref=%{commit}#/%{name}-%{shortcommit}.tar.gz
# Updated translations
Source1:	http://translationproject.org/latest/clisp/sv.po
# https://sourceforge.net/p/clisp/patches/35/
Patch0:		%{name}-db.patch
# https://sourceforge.net/p/clisp/patches/32/
Patch1:		%{name}-format.patch
# The encrypt and setkey functions are no longer available from glibc
Patch2:		%{name}-setkey.patch
# Adapt to changes in pari 2.11.0
Patch3:		%{name}-pari.patch

BuildRequires:	dbus-devel
BuildRequires:	emacs
BuildRequires:	fcgi-devel
BuildRequires:	ffcall-devel
BuildRequires:	gcc
BuildRequires:	gdbm-devel
BuildRequires:	gettext-devel
BuildRequires:	ghostscript
BuildRequires:	glibc-langpack-en
BuildRequires:	groff
BuildRequires:	gtk2-devel
BuildRequires:	libXaw-devel
BuildRequires:	libXft-devel
BuildRequires:	libdb-devel
BuildRequires:	libglade2-devel
BuildRequires:	libsigsegv-devel
BuildRequires:	libsvm-devel
BuildRequires:	libxcrypt-devel
BuildRequires:	pari-devel
BuildRequires:	pari-gp
BuildRequires:	pcre-devel
BuildRequires:	libpq-devel
BuildRequires:	readline-devel
BuildRequires:	zlib-devel

# 2018-02-26
# On s390x, it builds, but does not run properly:
# ./lisp.run -B . -N locale -E UTF-8 -Emisc 1:1 -Epathname 1:1 -norc -m 2MW -lp ../src/ -x '(and (load "../src/init.lisp") (sys::%saveinitmem) (ext::exit)) (ext::exit t)'
# *** stack smashing detected ***: <unknown> terminated
ExcludeArch:	s390x

Requires:	emacs-filesystem
Requires:	vim-filesystem

# clisp contains a copy of gnulib, which has been granted a bundling exception:
# https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Packages_granted_exceptions
Provides:	bundled(gnulib)

%description
ANSI Common Lisp is a high-level, general-purpose programming
language.  GNU CLISP is a Common Lisp implementation by Bruno Haible
of Karlsruhe University and Michael Stoll of Munich University, both
in Germany.  It mostly supports the Lisp described in the ANSI Common
Lisp standard.  It runs on most Unix workstations (GNU/Linux, FreeBSD,
NetBSD, OpenBSD, Solaris, Tru64, HP-UX, BeOS, NeXTstep, IRIX, AIX and
others) and on other systems (Windows NT/2000/XP, Windows 95/98/ME)
and needs only 4 MiB of RAM.

It is Free Software and may be distributed under the terms of GNU GPL,
while it is possible to distribute commercial proprietary applications
compiled with GNU CLISP.

The user interface comes in English, German, French, Spanish, Dutch,
Russian and Danish, and can be changed at run time.  GNU CLISP
includes an interpreter, a compiler, a debugger, CLOS, MOP, a foreign
language interface, sockets, i18n, fast bignums and more.  An X11
interface is available through CLX, Garnet, CLUE/CLIO.  GNU CLISP runs
Maxima, ACL2 and many other Common Lisp packages.


%package devel
Summary:	Development files for CLISP
Provides:	%{name}-static = %{version}-%{release} 
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	libsigsegv-devel%{?_isa}

%description devel
Files necessary for linking CLISP programs.


%prep
%autosetup -p0 -n %{name}-%{commit}-%{commit}

# Change URLs not affected by the --hyperspec argument to configure
sed -i.orig 's|lisp.org/HyperSpec/Body/chap-7.html|lispworks.com/documentation/HyperSpec/Body/07_.htm|' \
    src/clos-package.lisp
touch -r src/clos-package.lisp.orig src/clos-package.lisp
rm -f src/clos-package.lisp.orig
for f in src/_README.*; do
  sed -i.orig 's|lisp.org/HyperSpec/FrontMatter|lispworks.com/documentation/HyperSpec/Front|' $f
  touch -r ${f}.orig $f
  rm -f ${f}.orig
done

# We only link against libraries in system directories, so we need -L dir in
# place of -Wl,-rpath -Wl,dir
cp -p src/build-aux/config.rpath config.rpath.orig
sed -i -e 's/${wl}-rpath ${wl}/-L/g' src/build-aux/config.rpath

# Fix modules that need access to symbols in libgnu.a
sed -i 's/\(${GLLIB_A}\) \(${LIBS}\)/-Wl,--whole-archive \1 -Wl,--no-whole-archive \2/' src/makemake.in

# Enable firefox to be the default browser for displaying documentation
sed -i 's/;; \((setq \*browser\* .*)\)/\1/' src/cfgunix.lisp

# Unpack the CLX manual
tar -C modules/clx -xzf modules/clx/clx-manual.tar.gz
chmod -R go+r modules/clx/clx-manual
chmod a-x modules/clx/clx-manual/html/doc-index.cgi

# Update the translations
cp -p %{SOURCE1} src/po

%build
ulimit -s unlimited
export LC_ALL=C.UTF-8

# Do not need to specify base modules: i18n, readline, regexp, syscalls.
# The dirkey module currently can only be built on Windows/Cygwin/MinGW.
# The editor module is not in good enough shape to use.
# The matlab, netica, and oracle modules require proprietary code to build.
# The queens module is intended as an example only, not for actual use.
./configure --prefix=%{_prefix} \
	    --libdir=%{_libdir} \
	    --mandir=%{_mandir} \
	    --infodir=%{_infodir} \
	    --docdir=%{_pkgdocdir} \
	    --fsstnd=redhat \
	    --hyperspec=http://www.lispworks.com/documentation/HyperSpec/ \
	    --with-module=asdf \
	    --with-module=berkeley-db \
	    --with-module=bindings/glibc \
	    --with-module=clx/new-clx \
	    --with-module=dbus \
	    --with-module=fastcgi \
	    --with-module=gdbm \
	    --with-module=gtk2 \
	    --with-module=libsvm \
	    --with-module=pari \
	    --with-module=pcre \
	    --with-module=postgresql \
	    --with-module=rawsock \
	    --with-module=zlib \
	    --with-libreadline-prefix=$PWD/readline \
	    --with-ffcall \
	    --cbcx \
	    build \
	    CPPFLAGS="-I/usr/include/libsvm" \
	    CFLAGS="%{optflags} -Wa,--noexecstack" \
	    LDFLAGS="-Wl,--as-needed -Wl,-z,relro -Wl,-z,noexecstack"

%install
ulimit -s unlimited
make -C build DESTDIR=%{buildroot} install
cp -a build/full %{buildroot}%{_libdir}/%{instdir}
rm -f %{buildroot}%{_pkgdocdir}/doc/clisp.{dvi,1,ps}
rm -f %{buildroot}%{_pkgdocdir}/{COPYRIGHT,GNU-GPL}
cp -p doc/mop-spec.pdf %{buildroot}%{_pkgdocdir}/doc
cp -p doc/*.png %{buildroot}%{_pkgdocdir}/doc
cp -p doc/Why-CLISP* %{buildroot}%{_pkgdocdir}/doc
cp -p doc/regexp.html %{buildroot}%{_pkgdocdir}/doc
find %{buildroot}%{_libdir} -name '*.dvi' | xargs rm -f
%find_lang %{name}
%find_lang %{name}low
cat %{name}low.lang >> %{name}.lang

# Compile the Emacs interface
pushd %{buildroot}%{_datadir}/emacs/site-lisp
%{_emacs_bytecompile} *.el
popd

# Put back the original config.rpath, and fix executable bits
cp -p config.rpath.orig %{buildroot}%{_libdir}/%{instdir}/build-aux/config.rpath
chmod a+x \
  %{buildroot}%{_libdir}/%{instdir}/build-aux/config.guess \
  %{buildroot}%{_libdir}/%{instdir}/build-aux/config.sub \
  %{buildroot}%{_libdir}/%{instdir}/build-aux/depcomp \
  %{buildroot}%{_libdir}/%{instdir}/build-aux/install-sh \
# Fix paths in the Makefiles
for mk in $(find %{buildroot}%{_libdir} -name Makefile); do
  sed -e "s,$PWD/modules,%{_libdir}/%{instdir}," \
      -e "s,$PWD/build/clisp,%{_bindir}/clisp," \
      -e "s,$PWD/build/linkkit,%{_libdir}/%{instdir}/linkkit," \
      -i $mk
done
for mk in %{buildroot}%{_libdir}/%{instdir}/{base,full}/makevars; do
  sed -e "s, -I$PWD[^']*,," \
      -e "s,%{_libdir}/lib\([[:alnum:]]*\)\.so,-l\1,g" \
      -i $mk
done

# Install config.h, which is needed in some cases
for dir in %{buildroot}%{_libdir}/%{instdir}/*; do
  cp -p build/$(basename $dir)/config.h $dir || :
done
cp -p build/config.h %{buildroot}%{_libdir}/%{instdir}
cp -p build/clx/new-clx/config.h \
   %{buildroot}%{_libdir}/%{instdir}/clx/new-clx

# Fix permissions
chmod 0755 %{buildroot}%{_bindir}/%{name}
chmod 0755 %{buildroot}%{_libdir}/%{instdir}/full/lisp.run

# Fix broken symlinks in the full set
pushd %{buildroot}%{_libdir}/%{instdir}/full
for obj in bogomips calls gettext readline regexi; do
  rm -f ${obj}.o
  ln -s ../base/${obj}.o ${obj}.o
done
for obj in libgnu libnoreadline lisp; do
  rm -f ${obj}.a
  ln -s ../base/${obj}.a ${obj}.a
done
for obj in fastcgi fastcgi_wrappers; do
  rm -f ${obj}.o
  ln -s ../fastcgi/${obj}.o ${obj}.o
done
rm -f bdb.o
ln -s ../berkeley-db/bdb.o bdb.o
rm -f clx.o
ln -s ../clx/new-clx/clx.o clx.o
rm -f cpcre.o
ln -s ../pcre/cpcre.o cpcre.o
rm -f dbus.o
ln -s ../dbus/dbus.o dbus.o
rm -f gdbm.o
ln -s ../gdbm/gdbm.o gdbm.o
rm -f gtk.o
ln -s ../gtk2/gtk.o gtk.o
rm -f libsvm.o
ln -s ../libsvm/libsvm.o libsvm.o
rm -f linux.o
ln -s ../bindings/glibc/linux.o linux.o
rm -f postgresql.o
ln -s ../postgresql/postgresql.o postgresql.o
rm -f rawsock.o
ln -s ../rawsock/rawsock.o rawsock.o
rm -f zlib.o
ln -s ../zlib/zlib.o zlib.o
popd

# Help the debuginfo generator
ln -s ../../src/modules.c build/base/modules.c
ln -s ../../src/modules.c build/full/modules.c

%files -f %{name}.lang
%license COPYRIGHT GNU-GPL
%{_bindir}/clisp
%{_mandir}/man1/clisp.1*
%{_pkgdocdir}/
%dir %{_libdir}/%{instdir}/
%dir %{_libdir}/%{instdir}/asdf/
%{_libdir}/%{instdir}/asdf/asdf.fas
%dir %{_libdir}/%{instdir}/base/
%{_libdir}/%{instdir}/base/lispinit.mem
%{_libdir}/%{instdir}/base/lisp.run
%dir %{_libdir}/%{instdir}/berkeley-db/
%{_libdir}/%{instdir}/berkeley-db/*.fas
%dir %{_libdir}/%{instdir}/bindings/
%dir %{_libdir}/%{instdir}/bindings/glibc/
%{_libdir}/%{instdir}/bindings/glibc/*.fas
%dir %{_libdir}/%{instdir}/clx/
%dir %{_libdir}/%{instdir}/clx/new-clx/
%{_libdir}/%{instdir}/clx/new-clx/*.fas
%{_libdir}/%{instdir}/data/
%dir %{_libdir}/%{instdir}/dbus/
%{_libdir}/%{instdir}/dbus/*.fas
%{_libdir}/%{instdir}/dynmod/
%dir %{_libdir}/%{instdir}/fastcgi/
%{_libdir}/%{instdir}/fastcgi/*.fas
%dir %{_libdir}/%{instdir}/full/
%{_libdir}/%{instdir}/full/lispinit.mem
%{_libdir}/%{instdir}/full/lisp.run
%dir %{_libdir}/%{instdir}/gdbm/
%{_libdir}/%{instdir}/gdbm/*.fas
%dir %{_libdir}/%{instdir}/gtk2/
%{_libdir}/%{instdir}/gtk2/*.fas
%dir %{_libdir}/%{instdir}/libsvm/
%{_libdir}/%{instdir}/libsvm/*.fas
%dir %{_libdir}/%{instdir}/pari/
%{_libdir}/%{instdir}/pari/*.fas
%dir %{_libdir}/%{instdir}/pcre/
%{_libdir}/%{instdir}/pcre/*.fas
%dir %{_libdir}/%{instdir}/postgresql/
%{_libdir}/%{instdir}/postgresql/*.fas
%dir %{_libdir}/%{instdir}/rawsock/
%{_libdir}/%{instdir}/rawsock/*.fas
%dir %{_libdir}/%{instdir}/zlib/
%{_libdir}/%{instdir}/zlib/*.fas
%{_datadir}/emacs/site-lisp/*
%{_datadir}/vim/vimfiles/after/syntax/*

%files devel
%doc modules/clx/clx-manual
%{_bindir}/clisp-link
%{_mandir}/man1/clisp-link.1*
%{_libdir}/%{instdir}/asdf/Makefile
%{_libdir}/%{instdir}/asdf/*.lisp
%{_libdir}/%{instdir}/asdf/*.sh
%{_libdir}/%{instdir}/base/*.a
%{_libdir}/%{instdir}/base/*.h
%{_libdir}/%{instdir}/base/*.o
%{_libdir}/%{instdir}/base/makevars
%{_libdir}/%{instdir}/berkeley-db/Makefile
%{_libdir}/%{instdir}/berkeley-db/*.h
%{_libdir}/%{instdir}/berkeley-db/*.lisp
%{_libdir}/%{instdir}/berkeley-db/*.o
%{_libdir}/%{instdir}/berkeley-db/*.sh
%{_libdir}/%{instdir}/bindings/glibc/Makefile
%{_libdir}/%{instdir}/bindings/glibc/*.lisp
%{_libdir}/%{instdir}/bindings/glibc/*.o
%{_libdir}/%{instdir}/bindings/glibc/*.sh
%{_libdir}/%{instdir}/build-aux/
%{_libdir}/%{instdir}/clx/new-clx/demos/
%{_libdir}/%{instdir}/clx/new-clx/README
%{_libdir}/%{instdir}/clx/new-clx/Makefile
%{_libdir}/%{instdir}/clx/new-clx/*.h
%{_libdir}/%{instdir}/clx/new-clx/*.lisp
%{_libdir}/%{instdir}/clx/new-clx/*.o
%{_libdir}/%{instdir}/clx/new-clx/*.sh
%{_libdir}/%{instdir}/config.h
%{_libdir}/%{instdir}/dbus/Makefile
%{_libdir}/%{instdir}/dbus/*.h
%{_libdir}/%{instdir}/dbus/*.lisp
%{_libdir}/%{instdir}/dbus/*.o
%{_libdir}/%{instdir}/dbus/*.sh
%{_libdir}/%{instdir}/fastcgi/README
%{_libdir}/%{instdir}/fastcgi/Makefile
%{_libdir}/%{instdir}/fastcgi/*.h
%{_libdir}/%{instdir}/fastcgi/*.lisp
%{_libdir}/%{instdir}/fastcgi/*.o
%{_libdir}/%{instdir}/fastcgi/*.sh
%{_libdir}/%{instdir}/full/*.a
%{_libdir}/%{instdir}/full/*.h
%{_libdir}/%{instdir}/full/*.o
%{_libdir}/%{instdir}/full/makevars
%{_libdir}/%{instdir}/gdbm/Makefile
%{_libdir}/%{instdir}/gdbm/*.h
%{_libdir}/%{instdir}/gdbm/*.lisp
%{_libdir}/%{instdir}/gdbm/*.o
%{_libdir}/%{instdir}/gdbm/*.sh
%{_libdir}/%{instdir}/gtk2/Makefile
%{_libdir}/%{instdir}/gtk2/*.cfg
%{_libdir}/%{instdir}/gtk2/*.glade
%{_libdir}/%{instdir}/gtk2/*.h
%{_libdir}/%{instdir}/gtk2/*.lisp
%{_libdir}/%{instdir}/gtk2/*.o
%{_libdir}/%{instdir}/gtk2/*.sh
%{_libdir}/%{instdir}/libsvm/README
%{_libdir}/%{instdir}/libsvm/Makefile
%{_libdir}/%{instdir}/libsvm/*.h
%{_libdir}/%{instdir}/libsvm/*.lisp
%{_libdir}/%{instdir}/libsvm/*.o
%{_libdir}/%{instdir}/libsvm/*.sh
%{_libdir}/%{instdir}/linkkit/
%{_libdir}/%{instdir}/pari/README
%{_libdir}/%{instdir}/pari/Makefile
%{_libdir}/%{instdir}/pari/*.h
%{_libdir}/%{instdir}/pari/*.lisp
%{_libdir}/%{instdir}/pari/*.o
%{_libdir}/%{instdir}/pari/*.sh
%{_libdir}/%{instdir}/pcre/Makefile
%{_libdir}/%{instdir}/pcre/*.h
%{_libdir}/%{instdir}/pcre/*.lisp
%{_libdir}/%{instdir}/pcre/*.o
%{_libdir}/%{instdir}/pcre/*.sh
%{_libdir}/%{instdir}/postgresql/README
%{_libdir}/%{instdir}/postgresql/Makefile
%{_libdir}/%{instdir}/postgresql/*.h
%{_libdir}/%{instdir}/postgresql/*.lisp
%{_libdir}/%{instdir}/postgresql/*.o
%{_libdir}/%{instdir}/postgresql/*.sh
%{_libdir}/%{instdir}/rawsock/demos/
%{_libdir}/%{instdir}/rawsock/Makefile
%{_libdir}/%{instdir}/rawsock/*.h
%{_libdir}/%{instdir}/rawsock/*.lisp
%{_libdir}/%{instdir}/rawsock/*.o
%{_libdir}/%{instdir}/rawsock/*.sh
%{_libdir}/%{instdir}/zlib/Makefile
%{_libdir}/%{instdir}/zlib/*.h
%{_libdir}/%{instdir}/zlib/*.lisp
%{_libdir}/%{instdir}/zlib/*.o
%{_libdir}/%{instdir}/zlib/*.sh
%{_datadir}/aclocal/clisp.m4


%changelog
* Fri Aug 10 2018 Jerry James <loganjerry@gmail.com> - 2.49.93-3.90b3631git
- Update to latest git snapshot for bug fixes

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.49.93-2.d1310adgit
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 21 2018 Jerry James <loganjerry@gmail.com> - 2.49.93-1.d1310adgit
- License change: GPLv2 to GPLv2+
- Build with readline 6 due to the new license
- Drop upstreamed -arm, -libsvm, -alias, and -linux patches
- Build for all architectures
- Bring back the pari module

* Mon Feb 26 2018 Tom Callaway <spot@fedoraproject.org> - 2.49.93-0.1.20180224hg
- update to latest in mercurial (lots of fixes)
- re-enable ppc64, aarch64
- disable s390x (builds, but does not run properly)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-27.20170224hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Jan 21 2018 Björn Esser <besser82@fedoraproject.org> - 2.49-26.20170224hg
- Explicitly BR: ffcall-devel and configure --with-ffcall

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 2.49-25.20170224hg
- Rebuilt for switch to libxcrypt

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-24.20170224hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-23.20170224hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 24 2017 Jerry James <loganjerry@gmail.com> - 2.49-22.20170224hg
- Update to latest mercurial snapshot
- Drop upstreamed -32bit patch
- Add -volatile, -negshift, and -alias patches

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-22.20161113hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Jan 28 2017 Jerry James <loganjerry@gmail.com> - 2.49-21.20161113hg
- Update to latest mercurial snapshot

* Fri Nov 11 2016 Jerry James <loganjerry@gmail.com> - 2.49-20.20161111hg
- Update to latest mercurial snapshot (bz 1392563)
- Drop upstreamed -gcc5 patch
- Rebase all other patches
- Update config.guess and config.sub

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.49-19.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 29 2015 Jerry James <loganjerry@gmail.com> - 2.49-18.20130208hg
- Install the full link set
- Fix installed Makefile paths
- Fix clx manual permissions

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-17.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr  3 2015 Jerry James <loganjerry@gmail.com> - 2.49-16.20130208hg
- Fix modules that need access to symbols in libgnu.a

* Wed Feb 11 2015 Jerry James <loganjerry@gmail.com> - 2.49-15.20130208hg
- Add -gcc5 patch to fix 32-bit build with gcc 5.0
- Use license macro

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-14.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-13.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Aug 30 2013 Jerry James <loganjerry@gmail.com> - 2.49-11.20130208hg
- clisp does not support aarch64 (bz 925155)
- Adapt to versionless docdir (bz 992605 and 993701)
- More stack space needed to install

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-11.20130208hg
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.49-10.20130208hg
- Perl 5.18 rebuild

* Mon Feb 18 2013 Jerry James <loganjerry@gmail.com> - 2.49-9.20130208hg
- Update to mercurial snapshot to fix FTBFS
- Drop upstreamed -hostname patch
- Build against libdb instead of libdb4
- Include the CLX manual in the -devel documentation
- Compile the Emacs Lisp interface
- Build the asdf module

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 25 2012 Jerry James <loganjerry@gmail.com> - 2.49-8
- Fix build for new libdb4-devel package.
- Fix ARM assembly (bz 812928)
- Add gnulib Provides (bz 821747)
- Disable the pari module for now; it does not compile against pari 2.5

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Mar 18 2012 Daniel E. Wilson <danw@bureau-13.org> - 2.49-6
- Changed build process to define the default browser.
- Fixed module directories to move only *.fas files.
- Moved build-aux directory to the development package.
- Replaced the clisp-* wildcards with the correct version.
- More stack space may be needed on all arches (Jerry James).

* Sun Jan  8 2012 Jerry James <loganjerry@gmail.com> - 2.49-5
- Rebuild for GCC 4.7
- Minor spec file cleanups

* Thu Jun 23 2011 Jerry James <loganjerry@gmail.com> - 2.49-4
- Add libsvm patch to fix FTBFS on Rawhide (bz 715970)
- Fix readline module to also use compat-readline5 instead of readline6
- Drop unnecessary spec file elements (clean script, etc.)

* Fri Feb 11 2011 Jerry James <loganjerry@gmail.com> - 2.49-3
- Build with compat-readline5 instead of readline (#511303)
- Build the libsvm module
- Get rid of the execstack flag on Lisp images

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.49-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Nov 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.49-1
- clisp-2.49 (#612469)
- -devel: Provides: %%name-static (#609602)

* Sun Nov 28 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.48-2
- rebuild (libsigsegv)

* Fri Feb 26 2010 Jerry James <loganjerry@gmail.com> - 2.48-1
- new release 2.48

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.47-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.47-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 22 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.47-1
- new release 2.47

* Wed Jul  2 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.46-1
- new release 2.46

* Fri Apr 18 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.44.1-1
- new release 2.44.1

* Fri Feb 22 2008 Gerard Milmeister <gemi@bluewin.ch> - 2.43-5
- Compile with -O0 to avoid GCC 4.3 miscompilation

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.43-4
- Autorebuild for GCC 4.3

* Sat Nov 24 2007 Gerard Milmeister <gemi@bluewin.ch> - 2.43-1
- new release 2.43

* Tue Oct 16 2007 Gerard Milmeister <gemi@bluewin.ch> - 2.42-1
- new release 2.42

* Fri May  4 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-6
- Revert to overriding stack limit in specfile

* Thu May  3 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-5
- Exclude ppc64 for now

* Mon Apr 30 2007 David Woodhouse <dwmw2@infradead.org> - 2.41-4
- Fix stack size in configure, restore ppc build

* Sat Dec  9 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.41-3
- rebuild without berkeley-db for now

* Fri Oct 13 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.41-1
- new version 2.41

* Tue Oct  3 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.40-3
- Added patch for x86_64

* Mon Oct  2 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.40-1
- new version 2.40

* Mon Aug 28 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-4
- Rebuild for FE6

* Fri Jul 28 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-3
- changed url to canonical web page

* Mon Jul 24 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-2
- rebuild with updated libsigsegv
- set CFLAGS to ""

* Mon Jul 17 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.39-1
- new version 2.39

* Fri Feb 17 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.38-2
- Rebuild for Fedora Extras 5

* Sun Jan 29 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.38-1
- new version 2.38

* Tue Jan  3 2006 Gerard Milmeister <gemi@bluewin.ch> - 2.37-1
- new version 2.37

* Wed Dec 28 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.36-1
- New Version 2.36

* Tue Aug 30 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.35-1
- New Version 2.35

* Thu Aug 18 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-5
- do the compilation in the "build" directory

* Thu Aug 18 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-4
- Use ulimit for the build to succeed on ppc

* Wed Aug 17 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-3
- Build fails on ppc, exclude for now

* Wed Aug 17 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-2
- Fix libdir for x86_64

* Tue Aug 16 2005 Gerard Milmeister <gemi@bluewin.ch> - 2.34-1
- New Version 2.34
