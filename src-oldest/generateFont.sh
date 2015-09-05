#!/bin/sh

# generateFont.sh TYPE STYLE STRIPES SIZE FAMILY 
# creates a new MetaFont file and then invokes it.
# Usage below.

# These environment variables are defaults,
# in case the command-line arguments are absent.
TYPE=${1-'p'}
STYLE=${2-'f'}
STRIPES=${3-'7'}
SIZE=${4-'10'}
SOURCE_MF_FAMILY=${5-'cmr'}
MAG=${6-'1.0'}

# Check the validity of the parameters.
if [ \( \( "$TYPE" != "b" \)  -a \( "$TYPE" != "p" \) \) \
     -o \( \( "$STYLE" != "b" \) -a \( "$STYLE" != "f" \) -a \( "$STYLE" != "h" \) \) ]; then
	echo "Usage: $0 TYPE STYLE STRIPES SIZE FAMILY MAG" >&2
	echo "       TYPE:    [b = bracket, p = parenthesis]" >&2
	echo "       STYLE:   [b = background, f = foreground, h = hydrid]" >&2
	echo "       STRIPES: [0-7]" >&2
	echo "       MAG:     [float]" >&2
	echo "       TEXMFHOME must be set" >&2
	exit 1
fi
case "$STRIPES" in
	"0") STRIPES_LETTER="a"
	;;
	"1") STRIPES_LETTER="b"
	;;
	"2") STRIPES_LETTER="c"
	;;
	"3") STRIPES_LETTER="d"
	;;
	"4") STRIPES_LETTER="e"
	;;
	"5") STRIPES_LETTER="f"
	;;
	"6") STRIPES_LETTER="g"
	;;
	"7") STRIPES_LETTER="h"
	;;
	*) echo "Usage: $0 TYPE STYLE STRIPES SIZE FAMILY" >&2
	   echo "       TYPE:    [b = bracket, p = parenthesis]" >&2
	   echo "       STYLE:   [b = background, f = foreground, h = hydrid]" >&2
	   echo "       STRIPES: [0-7]" >&2
	   echo "       TEXMFHOME must be set" >&2
	   exit 1
	;;
esac

SOURCE_FONT="${SOURCE_MF_FAMILY}${SIZE}"
DEST_MF_DIR="$TEXMFHOME/fonts/source/public/zetex"
DEST_MF="z${TYPE}${STYLE}${STRIPES_LETTER}${SOURCE_FONT}"
DEST_MF_PATH="${DEST_MF_DIR}/${DEST_MF}.mf"

# Check the validity of the source font.
if [ "" = "`kpsewhich ${SOURCE_FONT}.mf`" ]; then
	echo "$0: File \"${SOURCE_FONT}.mf\" does not exist" >&2
	exit 1
fi

# Check that the TEXMFHOME variable is set.
if [ "" = "$TEXMFHOME" ]; then
	echo "$0: Environment variable TEXMFHOME must be set" >&2
	exit 1
fi

mkdir -p $DEST_MF_DIR

if [ "" = "`kpsewhich $DEST_MF_PATH`" ]; then
	# Copied from rtest on p. 311 of the MetaFont book.
	echo "if unknown cmbase: input cmbase fi" > $DEST_MF_PATH
	echo "mode_setup;" >> $DEST_MF_PATH
	echo "def generate suffix t = enddef;" >> $DEST_MF_PATH
	echo "input ${SOURCE_FONT}; font_setup;" >> $DEST_MF_PATH
	echo "let iff = always_iff;" >> $DEST_MF_PATH

	echo "stripes:=$STRIPES;" >> $DEST_MF_PATH

	case $STYLE in
		"b") echo "foreground:=0;" >> $DEST_MF_PATH
		;;
		"f") echo "foreground:=1;" >> $DEST_MF_PATH
		;;
		"h") echo "foreground:=2;" >> $DEST_MF_PATH
		;;
	esac

	case $TYPE in
		"b") echo "input zeromanb;" >> $DEST_MF_PATH
		;;
		"p") echo "input zeromanp;" >> $DEST_MF_PATH
		;;
	esac
fi

# Generate a TFM file and 600pk file.
if [ "" = "`kpsewhich $DEST_MF.tfm`" ]; then
	mktextfm $DEST_MF   >> zetexfonts.log 2>&1
	mktexlsr $TEXMFHOME >> zetexfonts.log 2>&1
fi
# Generate a magnified pk file, if necessary
if [ "$MAG" != "1.0" ]; then
	echo "$MAG*$MAG*600+.5" > ____dpifile
	dpi=`bc < ____dpifile | sed -e 's/\..*//'`
	rm ____dpifile
	if [ "" = "`kpsewhich $DEST_MF.${dpi}pk`" ]; then
		dir=`kpsewhich $DEST_MF.600pk |sed -e 's;/[^/]*$;;'`
		mf-nowin -progname=mf "\\mode:=ljfour; mag:=$MAG; nonstopmode; input $DEST_MF" >> zetexfonts.log 2>&1
		gftopk "$DEST_MF.${dpi}gf" "$DEST_MF.${dpi}pk" >> zetexfonts.log 2>&1
		mv "$DEST_MF.${dpi}pk" "$dir"
		rm $DEST_MF.*
		mktexlsr $TEXMFHOME >> zetexfonts.log 2>&1
	fi
fi

exit 0
