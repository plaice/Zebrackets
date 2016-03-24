#!/usr/bin/python3

# File zebraFontFiles.py
#
# Copyright (c) Blanca Mancilla, John Plaice, 2015, 2016
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of the zebrackets package



str_zepunctb = '''def lb(expr mark_count, total_count) = 
    numeric wd#; wd#=max(5u#,4.5u#+.5if hefty:stem# else:rule_thickness# fi);
    beginchar(mark_count,wd#,body_height#,paren_depth#);

	if (foreground=0):
	    "zebracket- left bracket, background " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=1):
	    "zebracket- left bracket, foreground " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=2):
	    "zebracket- left bracket, hybrid " & decimal mark_count & "/" & decimal total_count;
	else:
	    "trouble city: invalid foreground type";
	fi;

	italcorr body_height#*slant;
	adjust_fit(0,0);
	numeric top_thickness,side_thickness;
	if hefty: top_thickness=vair;
	    side_thickness=max(crisp.breadth,stem-2stem_corr);
	else: top_thickness=side_thickness=rule_thickness; fi;
	pickup crisp.nib; pos1(side_thickness,0); pos2(side_thickness,0);
	top y1=h; bot y2=-d; lft x1l=lft x2l=hround(2.5u-.5side_thickness)-1-eps;
	filldraw stroke z1e--z2e;  % stem
	pos3(top_thickness,90); pos4(top_thickness,90);
	pos5(top_thickness,90); pos6(top_thickness,90);
	x3=x5=x1l; rt x4=rt x6=ceiling(w-.4u)+eps; y3r=y4r=y1; y5l=y6l=y2;
	filldraw stroke z3e--z4e;  % upper bar
	filldraw stroke z5e--z6e;  % lower bar

	if (foreground=0) or (foreground=2):
	    pickup pensquare scaled .6pt;
	    lft x7 = lft x1 - .1w;
	    rt x8 = rt x1 + .1w;
	fi;

	if (foreground=2):
	    for bitpos := 0 upto (total_count - 1):
		y7 := y8 := ((bitpos+1)/(total_count+1))[y1,y2];
		erase draw z7 -- z8;
	    endfor;
	fi;

	if (foreground=1) or (foreground=2):
		pickup pencircle scaled .25pt;
		x7 := lft x1 - .2w;
		x8 := x4 - .1w;
	fi;
			
	for bitpos := 0 upto (total_count - 1):
	    if ((mark_count mod (2**(bitpos+1))) >= (2**bitpos)): 
		y7 := y8 := ((bitpos+1)/(total_count+1))[y1,y2];
		if (foreground=0):
		    erase draw z7 -- z8;
		else:
		    draw z7 -- z8;
		fi;
	    fi;
	endfor;
	
	penlabels(1,2,3,4,5,6,7,8); 
    endchar;
enddef;

def rb(expr mark_count, total_count) = 
    numeric wd#; wd#=max(5u#,4.5u#+.5if hefty:stem# else:rule_thickness# fi);
    beginchar(mark_count + (2**total_count),wd#,body_height#,paren_depth#);

	if (foreground=0):
	    "zebracket- right bracket, background " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=1):
	    "zebracket- right bracket, foreground " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=2):
	    "zebracket- right bracket, hybrid " & decimal mark_count & "/" & decimal total_count;
	else:
	    "trouble city: invalid foreground type";
	fi;

	italcorr body_height#*slant-2u#+.5if hefty:stem# else:rule_thickness# fi;
	adjust_fit(0,0);
	numeric top_thickness,side_thickness;
	if hefty: top_thickness=vair;
	    side_thickness=max(crisp.breadth,stem-2stem_corr);
	else: top_thickness=side_thickness=rule_thickness; fi;
	pickup crisp.nib; pos1(side_thickness,0); pos2(side_thickness,0);
	top y1=h; bot y2=-d; rt x1r=rt x2r=hround(w-2.5u+.5side_thickness)+1+eps;
	filldraw stroke z1e--z2e;  % stem
	pos3(top_thickness,90); pos4(top_thickness,90);
	pos5(top_thickness,90); pos6(top_thickness,90);
	x3=x5=x1r; lft x4=lft x6=floor .4u-eps; y3r=y4r=y1; y5l=y6l=y2;
	filldraw stroke z3e--z4e;  % upper bar
	filldraw stroke z5e--z6e;  % lower bar
	
	if (foreground=0) or (foreground=2):
	    pickup pensquare scaled .6pt;
	    lft x7 = lft x1 - .1w;
	    rt x8 = rt x1 + .1w;
	fi;

	if (foreground=2):
	    for bitpos := 0 upto (total_count - 1):
		y7 := y8 := ((bitpos+1)/(total_count+1))[y1,y2];
		erase draw z7 -- z8;
	    endfor;
	fi;

	if (foreground=1) or (foreground=2):
	    pickup pencircle scaled .25pt;
	    x7 := x4 + .1w;
	    x8 := rt x1 + .2w;
	fi;
			
	for bitpos := 0 upto (total_count - 1):
	    if ((mark_count mod (2**(bitpos+1))) >= (2**bitpos)): 
		y7 := y8 := ((bitpos+1)/(total_count+1))[y1,y2];
		if (foreground=0):
		    erase draw z7 -- z8;
		else:
		    draw z7 -- z8;
		fi;
	    fi;
	endfor;
	
	penlabels(1,2,3,4,5,6,7,8); 
    endchar;
enddef;

for s := 0 upto ((2**slots)-1):
  lb(s,slots);
  rb(s,slots);
endfor;
'''

str_zepunctp = '''def lp(expr mark_count, total_count) =
    beginchar(mark_count,7u# if monospace: -u# fi,body_height#,paren_depth#);

	if (foreground = 0):
	    "zebracket- left parentheses, background " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=1):
	    "zebracket- left parentheses, foreground " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=2):
	    "zebracket- left parentheses, hybrid " & decimal mark_count & "/" & decimal total_count;
	else:
	    "trouble city: invalid foreground type";
	fi;

	italcorr body_height#*slant-.5u#;
	adjust_fit(0,0); pickup fine.nib;
	pos1(vair,0); pos2(.75[hair,stem],0); pos3(vair,0);
	rt x1r=rt x3r=hround(w-u); lft x2l=hround(x1-4u if monospace: +4/3u fi);
	top y1=h; y2=.5[y1,y3]=math_axis;
	filldraw stroke z1e{3(x2e-x1e),y2-y1}...z2e
	    ...{3(x3e-x2e),y3-y2}z3e;  % arc
	
	if  (foreground=0) or (foreground=2):
	    pickup pensquare scaled .6pt;
	    lft x5 = lft x2 - .1w;
	    rt x6 = rt x1 + .1w;
	fi;

	if (foreground=2):
	    for bitpos := 0 upto (total_count - 1):
		y5 := y6 := ((bitpos+1)/(total_count+1))[y1,y3];
		erase draw z5 -- z6;
	    endfor;
	fi;

	if (foreground=1) or (foreground=2):
	    pickup pencircle scaled .25pt;
	    x5 := lft x2 - .1w;
	    x6 := x1 - .1w;
	fi;

	for bitpos := 0 upto (total_count - 1):
	    if ((mark_count mod (2**(bitpos+1))) >= (2**bitpos)): 
		y5 := y6 := ((bitpos+1)/(total_count+1))[y1,y3];
		if (foreground = 0):
		    erase draw z5 -- z6;
		else:
		    draw z5 -- z6;
		fi;
	    fi;
	endfor;
	
	penlabels(1,2,3,5,6); 
    endchar;
enddef;

def rp(expr mark_count, total_count) =
    beginchar(mark_count + (2**total_count),7u# if monospace: -u# fi,body_height#,paren_depth#);

	if (foreground = 0):
	    "zebracket- right parentheses, background " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=1):
	    "zebracket- right parentheses, foreground " & decimal mark_count & "/" & decimal total_count;
	elseif (foreground=2):
	    "zebracket- right parentheses, hybrid " & decimal mark_count & "/" & decimal total_count;
	else:
	    "trouble city: invalid foreground type";
	fi;

	italcorr math_axis#*slant-.5u#;
	adjust_fit(0,0); pickup fine.nib;
	pos1(vair,0); pos2(.75[hair,stem],0); pos3(vair,0);
	lft x1l=lft x3l=hround u; rt x2r=hround(x1+4u if monospace: -4/3u fi);
	top y1=h; y2=.5[y1,y3]=math_axis;
	filldraw stroke z1e{3(x2e-x1e),y2-y1}...z2e
	    ...{3(x3e-x2e),y3-y2}z3e;  % arc
	
	if (foreground = 0) or (foreground=2):
	    pickup pensquare scaled .6pt;
	    lft x5 = lft x1 - .1w;
	    rt x6 = rt x2 + .1w;
	fi;

	if (foreground=2):
	    for bitpos := 0 upto (total_count - 1):
		y5 := y6 := ((bitpos+1)/(total_count+1))[y1,y3];
		erase draw z5 -- z6;
	    endfor;
	fi;

	if (foreground=1) or (foreground=2):
	    pickup pencircle scaled .25pt;
	    x5 := x1 + .1w;
	    x6 := rt x2 + .1w;
	fi;

	for bitpos := 0 upto (total_count - 1):
	    if ((mark_count mod (2**(bitpos+1))) >= (2**bitpos)): 
		y5 := y6 := ((bitpos+1)/(total_count+1))[y1,y3];
		if (foreground = 0):
		    erase draw z5 -- z6;
		else:
		    draw z5 -- z6;
		fi;
	    fi;
	endfor;
	
	penlabels(1,2,3,5,6); 
    endchar;
enddef;

for s := 0 upto ((2**slots)-1):
    lp(s,slots);
    rp(s,slots);
endfor;

%tracingequations:=tracingonline:=1;
%lp(1,4);
%rp(1,4);
'''

str_zeromanb = '''% The Computer Modern Roman family of fonts (by D. E. Knuth, 1979--1985)

if ligs>1: font_coding_scheme:="TeX text";
 spanish_shriek=oct"074"; spanish_query=oct"076";
else: font_coding_scheme:=if ligs=0: "TeX typewriter text"
  else: "TeX text without f-ligatures" fi;
 spanish_shriek=oct"016"; spanish_query=oct"017"; fi

mode_setup; font_setup;

input zepunctb;
% input accent;  % accents common to roman and italic text
% if ligs>1: input romlig; fi  % letter ligatures
% if ligs>0: input comlig; fi  % ligatures common with italic text
% if ligs<=1: input romsub; fi  % substitutes for ligatures

%%%ligtable "!": "`" =: spanish_shriek;
%%%ligtable "?": "`" =: spanish_query;
font_slant slant; font_x_height x_height#;
if monospace: font_normal_space 9u#; % no stretching or shrinking
 font_quad 18u#;
 font_extra_space 9u#;
else: font_normal_space 6u#+2letter_fit#;
 font_normal_stretch 3u#; font_normal_shrink 2u#;
 font_quad 18u#+4letter_fit#;
 font_extra_space 2u#;
 k#:=-.5u#; kk#:=-1.5u#; kkk#:=-2u#; % three degrees of kerning
%%% ligtable "k": if serifs: "v": "a" kern -u#, fi\\"w": "e" kern k#,
%%%  "a" kern k#, "o" kern k#, "c" kern k#;
%%% ligtable "P": "A" kern kk#,
%%%  "y": "o" kern k#, "e" kern k#, "a" kern k#, "." kern kk#, "," kern kk#;
%%% ligtable "F": "V": "W": if serifs: "o" kern kk#, "e" kern kk#, "u" kern kk#,
%%%    "r" kern kk#, "a" kern kk#, "A" kern kkk#,
%%%   else: "o" kern k#, "e" kern k#, "u" kern k#,
%%%    "r" kern k#, "a" kern k#, "A" kern kk#, fi
%%%  "K": "X": "O" kern k#, "C" kern k#, "G" kern k#, "Q" kern k#;
%%% ligtable "T": "y" kern if serifs: k# else: kk# fi,
%%%  "Y": "e" kern kk#, "o" kern kk#,
%%%   "r" kern kk#, "a" kern kk#, "A" kern kk#, "u" kern kk#;
%%% ligtable "O": "D": "X" kern k#, "W" kern k#, "A" kern k#,
%%%   "V" kern k#, "Y" kern k#;
%%% if serifs: ligtable "h": "m": "n":
%%%   "t" kern k#, "u" kern k#, "b" kern k#, "y" kern k#, "v" kern k#, "w" kern k#;
%%%  ligtable "c": "h" kern k#, "k" kern k#; fi
%%% ligtable "o": "b": "p": "e" kern -k#, "o" kern -k#, "x" kern k#,
%%%   "d" kern -k#, "c" kern -k#, "q" kern -k#,
%%%  "a": if serifs: "v" kern k#, "j" kern u#, else: "r" kern k#, fi
%%%  "t": "y" kern k#,
%%%  "u": "w" kern k#;
%%% ligtable "A": if serifs: "R": fi\\ "t" kern k#,
%%%  "C" kern k#, "O" kern k#, "G" kern k#, "U" kern k#, "Q" kern k#,
%%%  "L": "T" kern kk#, "Y" kern kk#, "V" kern kkk#, "W" kern kkk#;
%%% ligtable "g": "j" kern -k#; % logjam
%%% ligtable "I": "I" kern -k#;
 fi % Richard III
 % there are ligature/kern programs for |"f"| in the {\tt romlig} file
 % and for |"-"|, |"`"|, and |"'"| in the {\tt comlig} file
bye.
'''

str_zeromanp = '''% The Computer Modern Roman family of fonts (by D. E. Knuth, 1979--1985)

if ligs>1: font_coding_scheme:="TeX text";
 spanish_shriek=oct"074"; spanish_query=oct"076";
else: font_coding_scheme:=if ligs=0: "TeX typewriter text"
  else: "TeX text without f-ligatures" fi;
 spanish_shriek=oct"016"; spanish_query=oct"017"; fi

mode_setup; font_setup;

input zepunctp;
% input accent;  % accents common to roman and italic text
% if ligs>1: input romlig; fi  % letter ligatures
% if ligs>0: input comlig; fi  % ligatures common with italic text
% if ligs<=1: input romsub; fi  % substitutes for ligatures

%%%ligtable "!": "`" =: spanish_shriek;
%%%ligtable "?": "`" =: spanish_query;
font_slant slant; font_x_height x_height#;
if monospace: font_normal_space 9u#; % no stretching or shrinking
 font_quad 18u#;
 font_extra_space 9u#;
else: font_normal_space 6u#+2letter_fit#;
 font_normal_stretch 3u#; font_normal_shrink 2u#;
 font_quad 18u#+4letter_fit#;
 font_extra_space 2u#;
 k#:=-.5u#; kk#:=-1.5u#; kkk#:=-2u#; % three degrees of kerning
%%% ligtable "k": if serifs: "v": "a" kern -u#, fi\\"w": "e" kern k#,
%%%  "a" kern k#, "o" kern k#, "c" kern k#;
%%% ligtable "P": "A" kern kk#,
%%%  "y": "o" kern k#, "e" kern k#, "a" kern k#, "." kern kk#, "," kern kk#;
%%% ligtable "F": "V": "W": if serifs: "o" kern kk#, "e" kern kk#, "u" kern kk#,
%%%    "r" kern kk#, "a" kern kk#, "A" kern kkk#,
%%%   else: "o" kern k#, "e" kern k#, "u" kern k#,
%%%    "r" kern k#, "a" kern k#, "A" kern kk#, fi
%%%  "K": "X": "O" kern k#, "C" kern k#, "G" kern k#, "Q" kern k#;
%%% ligtable "T": "y" kern if serifs: k# else: kk# fi,
%%%  "Y": "e" kern kk#, "o" kern kk#,
%%%   "r" kern kk#, "a" kern kk#, "A" kern kk#, "u" kern kk#;
%%% ligtable "O": "D": "X" kern k#, "W" kern k#, "A" kern k#,
%%%   "V" kern k#, "Y" kern k#;
%%% if serifs: ligtable "h": "m": "n":
%%%   "t" kern k#, "u" kern k#, "b" kern k#, "y" kern k#, "v" kern k#, "w" kern k#;
%%%  ligtable "c": "h" kern k#, "k" kern k#; fi
%%% ligtable "o": "b": "p": "e" kern -k#, "o" kern -k#, "x" kern k#,
%%%   "d" kern -k#, "c" kern -k#, "q" kern -k#,
%%%  "a": if serifs: "v" kern k#, "j" kern u#, else: "r" kern k#, fi
%%%  "t": "y" kern k#,
%%%  "u": "w" kern k#;
%%% ligtable "A": if serifs: "R": fi\\ "t" kern k#,
%%%  "C" kern k#, "O" kern k#, "G" kern k#, "U" kern k#, "Q" kern k#,
%%%  "L": "T" kern kk#, "Y" kern kk#, "V" kern kkk#, "W" kern kkk#;
%%% ligtable "g": "j" kern -k#; % logjam
%%% ligtable "I": "I" kern -k#;
 fi % Richard III
 % there are ligature/kern programs for |"f"| in the {\tt romlig} file
 % and for |"-"|, |"`"|, and |"'"| in the {\tt comlig} file
bye.
'''

