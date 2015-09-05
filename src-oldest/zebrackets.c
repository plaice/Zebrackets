/*
  This filter is run on a region of text.
  Its arguments dictate translation of parentheses in the region.
*/

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef SETMAX
#define SETMAX(A,B)       if ((A) < (B)) {(A) = (B);}
#endif /* SETMAX */

#ifndef SETMIN
#define SETMIN(A,B)       if ((A) > (B)) {(A) = (B);}
#endif /* SETMIN */

#define INITIALBUFSIZE 4096

static char*    buffer;
static unsigned bufsize;
static unsigned buflast;
static unsigned where;
static int      stripes_numerator;
static int      stripes_denominator;

int (*valueFromEncoding) (int);
int (*valueToEncoding) (int);

typedef enum delimiterType
{
  BRACKET,
  PARENTHESIS
} delimType;

static struct delimiter
{
  char open, close;
  int depth;
  int count, index;    /* count is across all parens, index is per depth */
  int highestCount;    /* highest index so far in parse */
  int deepestDepth;    /* deepest depth in parse */
  int broadestBreadth; /* broadest breadth in parse */
  int numerator, denominator;
  char type;
  bool used;
  unsigned stack[64];
} delimiters[2];

int
power(int x, int n)
{
  int p = 1;

  while (n > 0)
  {
    p *= x;
    --n;
  }
  return (p);
}

int
valueToBinary (int value)
{
  return value % 256;
}

int
valueToUnary (int value)
{
  /* until NFSS, max is 7 stripes (wrap around or fold over) */
  return power(2, (value % 8)) - 1;
}

int
valueToDemux (int value)
{
  return power(2, value % 7);
}

int
valueFromBinary (int value)
{
  /* replace denominator with lg (base 2) value */
  return (int) (ceil(log((double) value) / log((double) 2.)));
}

int
valueFromUnary (int value)
{
  return value - 1;
}

int
valueFromDemux (int value)
{
  return value;
}

void
count_delimiters ()
{
  char c;

  /*
   * Go through the buffer and count the (opening) delimiters in case
   * automatic stripe denominator is requested 
   */

  for (where = 0; where != buflast; ++where)
  {
    c = buffer[where];

    /* check the open delimiters to count across */
    for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
    {
      if (c == delimiters[w].open || c == delimiters[w].close)
      {
        if (c == delimiters[w].open)
        {
          delimiters[w].used = true;
          delimiters[w].count++;
          SETMAX(delimiters[w].highestCount, delimiters[w].count);
          delimiters[w].depth++;
          delimiters[w].stack[delimiters[w].depth]++;
          SETMAX(delimiters[w].deepestDepth, delimiters[w].depth);
          SETMAX(delimiters[w].broadestBreadth,
                 delimiters[w].stack[delimiters[w].depth]);
    
        } /* c is open end */
        else
        { /* c is close end */
          delimiters[w].depth--;
        }
      } /* c is open or close end */
    } /* for each delimiter type */
  } /* while where != buflast */

  /* calculate all the denominators based upon above tally */
  for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
  {
    if (delimiters[w].used)
    {
      switch (stripes_numerator)
      {
        /* automatic (default) mode => use (unique) count */
        case -1:
          delimiters[w].denominator = delimiters[w].highestCount;
          break;

        /* depth */
        case -2:
          delimiters[w].denominator = delimiters[w].deepestDepth;
          break;

        /* breadth at given level */
        case -3:
          delimiters[w].denominator = delimiters[w].broadestBreadth;
          break;

        default:
          /* manual numerator style selected */
          delimiters[w].denominator = stripes_denominator;
      }

      delimiters[w].denominator =
        valueFromEncoding(delimiters[w].denominator);

      /* until nfss, max is 7 */
      SETMIN(delimiters[w].denominator, 7);
      fprintf(stderr, "denominator %d\n", delimiters[w].denominator);
    }
  } /* for each delimiter type */
}

void
replace_symbols (char style, char* typeFamily, int ptSize)
{
  enum side
  {
    LEFT,
    RIGHT
  }         end;     /* for opening or closing delimiter */
  int       which;   /* which delimiter (loop index) */
  bool      replace;
  delimType w;

  for (w = BRACKET; w <= PARENTHESIS; ++w)
  {
    delimiters[w].count = -1;
    delimiters[w].depth = 0;
    for (which = 0; which < 64; which++) 
      delimiters[w].stack[which] = 0;
  }

  for (where = 0; where != buflast; ++where)
  {
    replace = false;
    for (w = BRACKET; w <= PARENTHESIS; ++w)
    {
      if (buffer[where] == delimiters[w].open ||
          buffer[where] == delimiters[w].close)
      {
        if (buffer[where] == delimiters[w].open)
        {
          end = LEFT;
          delimiters[w].stack[delimiters[w].depth] = delimiters[w].count;
          delimiters[w].depth++;
          delimiters[w].index = 1;
          delimiters[w].count++;
        }
        else
        {
          end = RIGHT;
          delimiters[w].index--;
          delimiters[w].depth--;
        }
    
        replace = true;
        break;
      }
    } /* for each delimiter type */

    if (replace)
    {
      int numerator;
    
      switch (stripes_numerator)
      {
        /* automatic (default) mode => use (unique) count */
        case -1:
          if (end == LEFT)
            numerator = delimiters[w].count;
          else
            numerator = delimiters[w].stack[delimiters[w].depth] + 1;
          break;

        /* depth */
        case -2:
          if (end == LEFT)
            numerator = delimiters[w].depth - 1;
          else
            numerator = delimiters[w].depth;
          break;

        /* breadth at given level */
        case -3:
          numerator = delimiters[w].index;
          break;

        default:
          numerator = stripes_numerator;
      }
      numerator = valueToEncoding(numerator);
      if (end == RIGHT)
        numerator += power(2, delimiters[w].denominator);
      printf("{\\z%c%c%c%s%c \\symbol{%d}}",
             delimiters[w].type,
             style,
             'a' + delimiters[w].denominator,
             typeFamily,
             'A' - 1 + ptSize,
             numerator);
    }
    else
      printf("%c", buffer[where]);

  } /* for across input buffer */
}

void
generate_files(char type, char style, int stripes, int size, char* typeFamily)
{
  static char baseCommand[] = "/scripts/zetex/sh/generateFont.sh";
  char* texmfhome = getenv("TEXMFHOME");
  char* command = malloc(strlen(texmfhome) + strlen(baseCommand) + strlen(typeFamily) + 128);
  if (! command)
  {
    fprintf(stderr, "ran out of memory\n");
    exit(1);
  }
  sprintf(command, "%s%s %c %c %d %d %s",
          texmfhome, baseCommand, type, style, stripes, size, typeFamily);
  //fprintf(stderr, "%s\n", command);
  system(command);
  free(command);
}

void
read_input()
{
  bufsize = INITIALBUFSIZE;
  assert(bufsize);
  buffer = malloc(sizeof(char) * bufsize);
  buflast = 0;
  int c;
  if (! buffer)
  {
    fprintf(stderr, "ran out of memory\n");
    exit(1);
  }
  while ((c = getchar()) != EOF)
  {
    if (buflast == bufsize)
    {
      bufsize *= 2;
      buffer = realloc(buffer, bufsize);
      if (! buffer)
      {
        fprintf(stderr, "ran out of memory\n");
        exit(1);
      }
    }
    buffer[buflast++] = c;
  }
}

int
main(int argc, char* argv[])
{
  int  ptSize;              /* size of generated parens */
  char style;
  char* encoding;        /* {unary, binary} */
  char* typeFamily;

  delimiters[BRACKET].open = '[';
  delimiters[BRACKET].close = ']';
  delimiters[BRACKET].type = 'b';
  delimiters[PARENTHESIS].open = '(';
  delimiters[PARENTHESIS].close = ')';
  delimiters[PARENTHESIS].type = 'p';

  /* Read in the input, and check for validity. */
  for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
  {
    delimiters[w].count = 0;
    delimiters[w].used = false;
    delimiters[w].denominator = -1;        /* flagging error */
    delimiters[w].highestCount = 0;
    delimiters[w].deepestDepth = 0;
    delimiters[w].broadestBreadth = 0;
  } /* for each delimiter type */

  char* texmfhome = getenv("TEXMFHOME");
  if (texmfhome == NULL)
  {
    fprintf(stderr, "Environment variable TEXMFHOME must be set\n");
    exit(1);
  }

  if (argc != 7)
  {
    fprintf(stderr, "invalid number of arguments\n");
    exit(1);
  }
  if (1 != sscanf(argv[1], "%c", &style))
  {
    fprintf(stderr, "invalid style\n");
    exit(1);
  }
  if (1 != sscanf(argv[2], "%d", &stripes_numerator))
  {
    fprintf(stderr, "invalid numerator\n");
    exit(1);
  }
  if (1 != sscanf(argv[3], "%d", &stripes_denominator))
  {
    fprintf(stderr, "invalid denominator\n");
    exit(1);
  }
  encoding = argv[4];
  if (1 != sscanf(argv[5], "%d", &ptSize))
  {
    fprintf(stderr, "invalid point size\n");
    exit(1);
  }
  typeFamily = argv[6];

  switch (encoding[0])
  {
    /* binary */
    case 'b':
      valueToEncoding = valueToBinary;
      valueFromEncoding = valueFromBinary;
      break;

    /* unary */
    case 'u':
      valueToEncoding = valueToUnary;
      valueFromEncoding = valueFromUnary;
      break;

    /* demux */
    case 'd':
      valueToEncoding = valueToDemux;
      valueFromEncoding = valueFromDemux;
      break;

    default:
      fprintf(stderr, "invalid encoding\n");
      exit(1);
  }

  if (stripes_numerator < 0)
  {
    if (stripes_numerator < -3)
    {
      fprintf(stderr, "invalid numerator\n");
      exit(1);
    }
  }
  else
  {
    if (stripes_denominator < 0)
    {
      fprintf(stderr, "invalid denominator\n");
      exit(1);
    }
  }

  /* Now get to work. */

  read_input();
  count_delimiters();

  /* non-automatic mode */
  if (stripes_denominator != -1)
  {
    for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
    {
      delimiters[w].denominator = stripes_denominator;
    } /* for each delimiter type */
  }

  for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
  {
    if (delimiters[w].used)
    {
      char* fontName = malloc(sizeof(char) * (strlen(typeFamily) + 5));
      if (! fontName)
      {
        fprintf(stderr, "ran out of memory\n");
        exit(1);
      }
      sprintf(fontName, "z%c%c%c%s", 
              delimiters[w].type,
              style,
              'a' + delimiters[w].denominator,
              typeFamily);
      printf("\\ifundefined{%s%c}\\newfont{\\%s%c}{%s%d}\\fi\n", 
             fontName, 'A'-1+ptSize, fontName, 'A'-1+ptSize, fontName, ptSize);
      free(fontName);
    } /* used */
  } /* for each delimiter type */

  replace_symbols(style, typeFamily, ptSize);

  for (delimType w = BRACKET; w <= PARENTHESIS; ++w)
  {
    if (delimiters[w].used)
      generate_files(delimiters[w].type,
                     style,
                     delimiters[w].denominator, 
                     ptSize,
                     typeFamily);
  } /* for each delimiter type */

  /* release buffer */
  free(buffer);

  exit(0);
}
