#!/usr/bin/perl

$texmf = $ENV{'TEXMFHOME'};
if ($texmf eq "")
{
  die "Environment variable TEXMFHOME must be set\n";
}
$cbindir = $texmf . "/scripts/zetex/c";
$shbindir = $texmf . "/scripts/zetex/sh";

$filterMode = 0;

$buffer = ">/tmp/ze-buf";
$subBuffer = ">/tmp/ze-sub_buf";

open(BUFFER, $buffer)        || die "Can't open $buffer\n";
select(BUFFER); $| = 1;      # sets unbuffered
open(SUB_BUFFER, $subBuffer) || die "Can't open $subBuffer\n";
select(SUB_BUFFER); $| = 1;  # sets unbuffered

$defaultStyle = "";
$defaultNumerator = "";
$defaultDenominator = "";
$defaultEncoding = "";
$defaultSize = "";
$defaultFamily = "";
$defaultType = "";
$defaultStripes = "";
$defaultIndex = "";
$defaultMag = "";

while (<STDIN>)
{
  if ($filterMode == 0)
  {
    if ( /^\\zebracketsdefaults(\[.*])/ )
    {
      $args = $1 ;
      #print STDERR "$args\n";
      if ( /sty\w*=([bfh])\w*[,\]]/ )
      { $defaultStyle = $1; }
      if ( /num\w*=([-]?\d+)[,\]]/ )
      { $defaultNumerator = $1; }
      if ( /den\w*=([-]?\d+)[,\]]/ )
      { $defaultDenominator = $1; }
      if ( /enc\w*=(\w+)[,\]]/ )
      { $defaultEncoding = $1; }
      if ( /siz\w*=(\d+)[,\]]/ )
      { $defaultSize = $1; }
      if ( /fam\w*=(\w+)[,\]]/ )
      { $defaultFamily = $1; }
      if ( /str\w*=(\d+)[,\]]/ )
      { $defaultStripes = $1; }
      if ( /typ\w*=([bp])\w+[,\]]/ )
      { $defaultType = $1; }
      if ( /mag\w*=(\d+(\.\d+)*)[,\]]/ )
      { $defaultMag = $1; }
      if ( /ind\w*=([bdu])\w*[,\]]/ )
      {
        $defaultIndex = $1;
        if ($defaultIndex eq "b")
        { $defaultIndex = -3; }
        elsif ($defaultIndex eq "d")
        { $defaultIndex = -2; }
        else
        { $defaultIndex = -1; }
      }
    }
    elsif ( /^\\zebracketsfont(\[.*])/ )
    {
      $args = $1 ;
      #print STDERR "$args\n";
      if ( /typ\w*=([bp])\w*[,\]]/ )
      { $type = $1; }
      else
      { $type = $defaultType; }
      if ( /sty\w*=([bfh])\w*[,\]]/ )
      { $style = $1; }
      else
      { $style = $defaultStyle; }
      if ( /str\w*=(\d+)[,\]]/ )
      { $stripes = $1; }
      else
      { $stripes = $defaultStripes; }
      if ( /siz\w*=(\d+)[,\]]/ )
      { $size = $1; }
      else
      { $size = $defaultSize; }
      if ( /fam\w*=(\w+)[,\]]/ )
      { $family = $1; }
      else
      { $family = $defaultFamily; }
      if ( /mag\w*=(\d+(\.\d+)*)[,\]]/ )
      { $mag = sqrt($1); }
      elsif ($defaultMag != "")
      { $mag = sqrt($defaultMag); }
      else 
      { $mag = ""; }
      #print STDERR "generatefont.sh type=$type, style=$style, stripes=$stripes, size=$size, fam=$family, mag=$mag \n" ;
      system "$shbindir/generateFont.sh $type $style $stripes $size $family $mag > /tmp/generatefont.out";
    }
    elsif ( /^\\begin{zebrackets}(\[.*])/ )
    {
      $args = $1 ;
      #print STDERR "$args\n";
      if ( /sty\w*=([bfh])\w*[,\]]/ )
      { $style = $1; }
      else
      { $style = $defaultStyle; }
      if ( /ind\w*=([bdu])\w*[,\]]/ )
      {
        $index = $1;
        if ($index eq "b")
        { $index = -3; }
        elsif ($index eq "d")
        { $index = -2; }
        else
        { $index = -1; }
      }
      else
      { $index = $defaultIndex; }
      if ( /num\w*=([-]?\d+)[,\]]/ )
      { $numerator = $1; }
      else
      { $numerator = $defaultNumerator; }
      if ( /den\w*=([-]?\d+)[,\]]/ )
      { $denominator = $1; }
      else
      { $denominator = $defaultDenominator; }
      if ( /enc\w*=(\w+)[,\]]/ )
      { $encoding = $1; }
      else
      { $encoding = $defaultEncoding; }
      if ( /siz\w*=(\d+)[,\]]/ )
      { $size = $1; }
      else
      { $size = $defaultSize; }
      if ( /fam\w*=(\w+)[,\]]/ )
      { $family = $1; }
      else
      { $family = $defaultFamily; }
      if ($numerator eq "")
      { $numerator = $index; }
      if ($denominator eq "")
      { $denominator = -1; }
      #print STDERR "sty=$style, num=$numerator, den=$denominator, enc=$encoding, size=$size, fam=$family \n" ;
      $filterMode = 1;
    }
    # default is to append to main buffer
    else
    {
      print BUFFER $_;
    }
  }
  # otherwise we're writing to buffer which will be zebracketed
  else
  {
    if ( /^\\end{zebrackets}/ )
    {
      $filterMode = 0;
      close(SUB_BUFFER) || print "Can't close $subBuffer\n";

      #print STDERR "zebrackets sty=$style, num=$numerator, den=$denominator, enc=$encoding, size=$size, fam=$family \n" ;
      system "cat /tmp/ze-sub_buf | $cbindir/zebrackets $style $numerator $denominator $encoding $size $family > /tmp/ze-sub_buf-out";
      open(SUB_BUFFER_OUT, "</tmp/ze-sub_buf-out") || die "Can't open /tmp/ze-sub_buf-out\n";
      while (<SUB_BUFFER_OUT>)
      {
        print BUFFER $_;
      }
      open(SUB_BUFFER, $subBuffer) || die "Can't open $subBuffer\n";
    }
    else
    {
      print SUB_BUFFER $_;
    }
  }
}

close(BUFFER) || die "Can't close $buffer\n";
close(SUB_BUFFER) || die "Can't close $subBuffer\n";

open(BUFFER, "</tmp/ze-buf") || die "Can't open /tmp/ze-buf\n";
while (<BUFFER>)
{
  print STDOUT $_;
}

close(BUFFER) || die "Can't close /tmp/ze-buf\n";
