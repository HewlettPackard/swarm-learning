######################################################################
## (C)Copyright 2022 Hewlett Packard Enterprise Development LP
######################################################################


######################################################################
## We used to support a rather small set of docker container options
## for creating and managing the containers that we launch. This list
## has grown continuously until, now, we are at a point where we feel
## it is better to support the whole gamut. This script generates the
## code for two functions using the output of "docker container create
## --help":
##  1. parsing docker-related command line arguments; and
##  2. displaying help for docker-related command line arguments.
##
## Run "perl docker-opts.pl" to see the code that is generated.
######################################################################


# We use a little utility function, called matchDockerOpts, to look at the input
# command line parameter and tell us what set of docker options it matches. This
# set consists of either a single long-form option or several short-form ones.
# This function returns 0 for a succesful match and 1 for an unsuccessful one.
# This is easier than generating code for all permutations and combinations of
# short options - that is, we would rather not have separate switches for each
# of -d, -i, -t, -di, -dt, -id, -it, etc. To process using this method, we need:
# (a) a list of short and long options that we can feed to it; and then, (b) a
# case statement in a loop to process each option that is present in the output
# string. So, we first build these two requirements using separate variables and
# then, join them together to create the entire parsing function. getopt is very
# similar in functionality and, indeed, our original implementation used it. But
# we were unhappy with the way it handled missing and optional arguments and the
# way it separated the options from the arguments. The last straw that broke the
# camel's back was its insistence on making partial matches. Normally, we would
# have considered this a good thing but, when it insisted on treating --run as
# --runtime, it broke internal run of building continers.


# Set from the command line.
my ${sudo} = "";
${sudo} = shift @ARGV if (@ARGV);


# Code for the function that parses docker-related arguments.
my ${processFunc} = "";

# Long options start with a double dash. Example: --foo and --bar.
my ${longOptsList} = "";

# Short options start with a single dash, followed by a single letter or number.
# Example: -f and -b.
my ${shortOptsList} = "";
my ${caseLoop} = "";

# Code for the function that displays help for docker-related arguments.
my ${helpFunc} = "";

# Tag whether a line from the output of "docker content create --help" should be
# included in the body of our help function. We filter the output of the docker
# command and include only the part that is related to the set of options that
# it supports.
my ${includeInHelp} = 0;

# Pattern for parsing parameters that start with a leading double dash.
my $longOpt = "--([[:alnum:]_-]+)";

# Pattern for parsing parameters that start with a leading single dash.
my $shortOpt = "-([[:alnum:]])";

# Pattern for parsing arguments associated with the parameters. These are words
# like "string" and "list" that indicate the nature of acceptable arguments for
# the parameter.
my $arg = "([[:alnum:]_-]+)";

# Single whitespace character.
my $ws = "[[:space:]]";

# One or more whitespace characters.
my $multiWS = sprintf("%s+", ${ws});

# Optional (zero or more) whitespace characters.
my $optWS = sprintf("%s*", ${ws});

# A few of docker's parameters have aliases - that is, these parameters can be
# specified in more than one way. Typically, such parameters have two aliases -
# one that uses the long format and the other that uses the short one. Example:
# --env and -e refer to the same parameter. At the moment, docker does not have
# parameters that take more than two aliases. Therefore, our parsing logic too
# does not expect more than two aliases.

# There are a few inconsistencies between docker's reference documentation and
# the help text. For example, the reference documentation specifies both --net
# and --network as options to specify the container's network. In contrast, the
# help text specifies only --network. So, for the moment, this pattern will not
# match any of the inputs. But, just in case docker decides to fix things...
my $longLongOptWithArg = sprintf(
    # Matches: "--foo, --bar arg".
    "^%s%s,%s%s%s%s"
  , ${optWS}, ${longOpt}, ${optWS}, ${longOpt}, ${ws}, ${arg}
);

my $longLongOptWithoutArg = sprintf(
    # Matches: "--foo, --bar".
    "^%s%s,%s%s%s"
  , ${optWS}, ${longOpt}, ${optWS}, ${longOpt}, ${multiWS}
);

my $shortLongOptWithArg = sprintf(
    # Matches: "-f, --foo arg".
    "^%s%s,%s%s%s%s"
  , ${optWS}, ${shortOpt}, ${optWS}, ${longOpt}, ${ws}, ${arg}
);

my $shortLongOptWithoutArg = sprintf(
    # Matches: "-f, --foo".
    "^%s%s,%s%s%s"
  , ${optWS}, ${shortOpt}, ${optWS}, ${longOpt}, ${multiWS}
);

my $longOptWithArg = sprintf(
    # Matches: "--foo arg".
    "^%s%s%s%s"
  , ${optWS}, ${longOpt}, ${ws}, ${arg}
);

my ${longOptWithoutArg} = sprintf(
    # Matches: "--foo".
    "^%s%s%s"
  , ${optWS}, ${longOpt}, ${multiWS}
);

my ${shortOptWithArg} = sprintf(
    # Matches: "-f arg".
    "^%s%s%s%s"
  , ${optWS}, ${shortOpt}, ${ws}, ${arg}
);

my ${shortOptWithoutArg} = sprintf(
    # Matches: "-f".
    "^%s%s%s"
  , ${optWS}, ${shortOpt}, ${multiWS}
);

my ${help} = sprintf("^%s--help", ${optWS});

my ${startOfOptions} = "^Options:\$";

# Indent level for the parser function.
my ${pfIndent} = 0;

# Indent level for the help function.
my ${hfIndent} = 0;
my ${shiftWidth} = 4;


# Start generating the parser function.
${processFunc} .= "declare -a longOptsList\n";
${processFunc} .= "declare -a shortOptsList\n";
${processFunc} .= "\n";
${processFunc} .= "\n";

# Our getopt-replacement utility.
${processFunc} .= "matchDockerOpts()\n";
${processFunc} .= "{\n";
${pfIndent} += ${shiftWidth};

${processFunc} .= sprintf("%${pfIndent}sdeclare -a matches\n", " ");
${processFunc} .= "\n";

${processFunc} .= sprintf("%${pfIndent}sfor opt in \"\${@}\"\n", " ");
${processFunc} .= sprintf("%${pfIndent}sdo\n", " ");
${pfIndent} += ${shiftWidth};

# First, check whether this is a long option.
${processFunc} .= sprintf(
    "%${pfIndent}sif hasItem longOptsList \"\" \"\${opt}\" \"q\" \"y\"\n", " "
);
${processFunc} .= sprintf("%${pfIndent}sthen\n", " ");
${pfIndent} += ${shiftWidth};

${processFunc} .= sprintf("%${pfIndent}smatches+=(\"\${opt}\")\n", " ");

${pfIndent} -= ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}selse\n", " ");
${pfIndent} += ${shiftWidth};

# Not a long option. Check whether each character matches a short one. Note that
# we require a full match to return success. So, while -dit will return success,
# -ditz will fail because -z is not a valid docker short option (at the time of
# this writing). The sed statement converts the input parameter into a stream of
# short options: a single character with a single leading dash. For example, it
# converts -dit into -d, -i, and -t. Note that long forms cannot be clumped into
# a single word: --dit will result in a failure. This is because we do not want
# things like --capath to end up as docker options. We use printf, and not echo,
# because echo does not have --, the end-of-switches option. So, when we end up
# with something like echo "-e", the results are hilarious, though we were not
# particularly amused.
${processFunc} .= sprintf(
    "%${pfIndent}sfor char in \$(printf -- \"%%s\" \"\${opt}\" | sed -r 's/^-//;s/(.)/-\\1 /g')\n"
  , " "
);
${processFunc} .= sprintf("%${pfIndent}sdo\n", " ");
${pfIndent} += ${shiftWidth};

${processFunc} .= sprintf(
    "%${pfIndent}shasItem shortOptsList \"\" \"\${char}\" \"q\" \"y\" \\\n", " "
);
${pfIndent} += ${shiftWidth};
${processFunc} .= sprintf(
    "%${pfIndent}s&& matches+=(\"\${char}\") || return 1\n", " "
);
${pfIndent} -= ${shiftWidth};

${pfIndent} -= ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}sdone\n", " ");

${pfIndent} -= ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}sfi\n", " ");

${pfIndent} -= ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}sdone\n", " ");
${processFunc} .= "\n";

${processFunc} .= sprintf(
    "%${pfIndent}sprintf -- \"%%s \" \"\$\{matches[@]\}\"\n", " "
);
${processFunc} .= "\n";

${processFunc} .= sprintf("%${pfIndent}sreturn 0\n", " ");

${pfIndent} -= ${shiftWidth};
${processFunc} .= "}\n";
${processFunc} .= "\n";
${processFunc} .= "\n";

${processFunc} .= "processDockerBatchOpt()\n";
${processFunc} .= "{\n";
${pfIndent} += ${shiftWidth};

${processFunc} .= sprintf("%${pfIndent}slocal sidecar=\"\${1}\"\n", " ");
${processFunc} .= sprintf("%${pfIndent}slocal origParam=\"\${2}\"\n", " ");
${processFunc} .= sprintf("%${pfIndent}slocal opt=\"\${3}\"\n", " ");
${processFunc} .= sprintf("%${pfIndent}slocal optarg=\"\${4}\"\n", " ");
${processFunc} .= "\n";
${processFunc} .= sprintf(
    "%${pfIndent}s[[ -n \"\${sidecar}\" ]] && local sidecarPrefix=\"\${sidecar}-\"\n"
  , " "
);
${processFunc} .= "\n";

${processFunc} .= sprintf(
    "%${pfIndent}slocal optsList=\"\$(matchDockerOpts \"\${opt/\${sidecarPrefix}}\")\"\n"
  , " "
);
${processFunc} .= "\n";

# We cannot test the return code here. That code is the status of the assignment
# and not the matchDockerOpts function. So, its value will always be 0, success.
${processFunc} .= sprintf("%${pfIndent}sif [[ -z \"\${optsList}\" ]]\n", " ");
${processFunc} .= sprintf("%${pfIndent}sthen\n", " ");

${pfIndent} += ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}sunprocessedOpts+=(\"\${origParam}\")\n", " ");
${processFunc} .= sprintf("%${pfIndent}snShift=1\n", " ");
${processFunc} .= sprintf("%${pfIndent}sreturn 0\n", " ");
${pfIndent} -= ${shiftWidth};
${processFunc} .= sprintf("%${pfIndent}sfi\n", " ");
${processFunc} .= "\n";


# Start generating the case statement.
${caseLoop} .= sprintf("%${pfIndent}sfor anOpt in \${optsList}\n", " ");
${caseLoop} .= sprintf("%${pfIndent}sdo\n", " ");
${pfIndent} += ${shiftWidth};

${caseLoop} .= sprintf("%${pfIndent}slocal handlerFunc=\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg1=\"\${anOpt}\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg2=\"\${optarg}\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg3=\"\${anOpt}\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg4=\"dockerOpts\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg5=\"\${sidecarPrefix}\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg6=\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg7=\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal arg8=\n", " ");
${caseLoop} .= sprintf("%${pfIndent}slocal requireArg=\"y\"\n", " ");
${caseLoop} .= "\n";

${caseLoop} .= sprintf("%${pfIndent}scase \"\${anOpt}\" in\n", " ");
${pfIndent} += ${shiftWidth};


# Start generating the help function.
${helpFunc} .= "printDockerUsage()\n";
${helpFunc} .= "{\n";

${hfIndent} += ${shiftWidth};
${helpFunc} .= sprintf("%${hfIndent}sprintf -- \"Docker Options:\\n\"\n", " ");
${helpFunc} .= sprintf(
    "%${hfIndent}sprintf -- \"This tool accepts all \\\"docker container create\\\" options\\n\"\n"
  , " "
);
${helpFunc} .= sprintf("%${hfIndent}scat << __EOF\n", " ");


# https://perldoc.perl.org/functions/open#Assigning-a-filehandle-to-a-bareword.
# We seem to have a version of perl that accepts only the legacy form. This:
#       open(my ${helpOutput}, "-|", "docker container create --help");
#       while (<${helpOutput}>)
#       {
#           printf("LINE: %s\n", $_);
#       }
# produces:
#       LINE: GLOB(0x5610a45714d8)
# We should probably switch to the readline function.
open(helpOutput, "-|", "${sudo} docker container create --help") or die $!;

# Parse docker's output and generate appropriate code for our two functions.
while (<helpOutput>)
{
    # Ignore the help parameter.
    next if (/${help}/);

    # The order of these two statements is important. Switching it will result
    # in a line that says, "Options:" being included in the help text.
    ${helpFunc} .= $_ if (${includeInHelp});
    ${includeInHelp} = 1 if (/${startOfOptions}/);

    if (/${longLongOptWithArg}/)
    {
        ${longOptsList} .= "--$1 --$2 ";
        ${caseLoop} .= sprintf "%${pfIndent}s--%s|--%s)\n", " ", $1, $2;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $2
        );
        ${caseLoop} .= sprintf("%${pfIndent}sarg3=\"--%s\"\n", " ", $2);
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${longLongOptWithoutArg}/)
    {
        ${longOptsList} .= "--$1 --$2 ";
        ${caseLoop} .= sprintf "%${pfIndent}s--%s|--%s)\n", " ", $1, $2;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $1, $2
        );
        ${caseLoop} .= sprintf("%${pfIndent}sarg3=\"--%s\"\n", " ", $2);
        ${caseLoop} .= sprintf("%${pfIndent}srequireArg=\n", " ");
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${shortLongOptWithArg}/)
    {
        ${longOptsList} .= "--$1 --$2 ";
        ${shortOptsList} .= "-$1 ";
        ${caseLoop} .= sprintf("%${pfIndent}s-%s|--%s|--%s)\n", " ", $1, $1, $2);

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $2
        );
        ${caseLoop} .= sprintf("%${pfIndent}sarg3=\"--%s\"\n", " ", $2);
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${shortLongOptWithoutArg}/)
    {
        ${longOptsList} .= "--$1 --$2 ";
        ${shortOptsList} .= "-$1 ";
        ${caseLoop} .= sprintf("%${pfIndent}s-%s|--%s|--%s)\n", " ", $1, $1, $2);

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $2
        );
        ${caseLoop} .= sprintf("%${pfIndent}sarg3=\"--%s\"\n", " ", $2);
        ${caseLoop} .= sprintf("%${pfIndent}srequireArg=\n", " ");
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${longOptWithArg}/)
    {
        ${longOptsList} .= "--$1 ";
        ${caseLoop} .= sprintf "%${pfIndent}s--%s)\n", " ", $1;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\";;\n"
          , " ", $1
        );
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${longOptWithoutArg}/)
    {
        ${longOptsList} .= "--$1 ";
        ${caseLoop} .= sprintf "%${pfIndent}s--%s)\n", " ", $1;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $1
        );
        ${caseLoop} .= sprintf("%${pfIndent}srequireArg=\n", " ");
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${shortOptWithArg}/)
    {
        ${shortOptsList} .= "-$1 ";
        ${caseLoop} .= sprintf "%${pfIndent}s-%s|--%s)\n", " ", $1, $1;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\";;\n"
          , " ", $1
        );
        ${pfIndent} -= ${shiftWidth};
    }
    elsif (/${shortOptWithoutArg}/)
    {
        ${shortOptsList} .= "-$1 ";
        ${caseLoop} .= sprintf "%${pfIndent}s-%s|--%s)\n", " ", $1, $1;

        ${pfIndent} += ${shiftWidth};
        ${caseLoop} .= sprintf(
            "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase %s)Opt\"\n"
          , " ", $1
        );
        ${caseLoop} .= sprintf("%${pfIndent}srequireArg=\n", " ");
        ${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
        ${pfIndent} -= ${shiftWidth};
    }
}

close(helpOutput);

# Complete generating the case statement.
# --detach is not a "docker container create" option. We process it separately.
${longOptsList} .= "--d --detach ";
${shortOptsList} .= "-d ";
${caseLoop} .= sprintf("%${pfIndent}s-d|--d|--detach)\n", " ");
${pfIndent} += ${shiftWidth};
${caseLoop} .= sprintf(
    "%${pfIndent}shandlerFunc=\"processDocker\$(CamelCase detach)Opt\"\n", " "
);
${caseLoop} .= sprintf("%${pfIndent}sarg3=\"--detach\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}srequireArg=\n", " ");
${caseLoop} .= sprintf "%${pfIndent}s;;\n", " ";
${pfIndent} -= ${shiftWidth};

# This is unnecessary - we should not end up here. We have retained this code as
# a safety net and a bug catcher.
${caseLoop} .= sprintf(
    "%${pfIndent}s*) unprocessedOpts+=(\"\${origParam}\"); nShift=1;;\n", " "
);

${pfIndent} -= ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}sesac\n", " ");
${caseLoop} .= "\n";

${caseLoop} .= sprintf("%${pfIndent}sif [ -n \"\${handlerFunc}\" ]\n", " ");
${caseLoop} .= sprintf("%${pfIndent}sthen\n", " ");

${pfIndent} += ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}sif [ -z \"\${requireArg}\" ]\n", " ");
${caseLoop} .= sprintf("%${pfIndent}sthen\n", " ");

${pfIndent} += ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}shasOptarg \"\${arg2}\" && arg2=\"\${arg2,,}\" || arg2=\"true\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}sarg8=\"y\"\n", " ");
${caseLoop} .= sprintf("%${pfIndent}snShift=1\n", " ");

${pfIndent} -= ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}sfi\n", " ");
${caseLoop} .= "\n";

${caseLoop} .= sprintf("%${pfIndent}sarg3=\"\${arg3}=\"\n", " ");
${caseLoop} .= "\n";

# By default, we simply add all the parameters and their arguments to an array
# that is then fed to docker. However, we subject a few options to some special
# treatment. Invoke the custom handler function for such parameters.
${caseLoop} .= sprintf(
    "%${pfIndent}sdeclare -F \"\${handlerFunc}\" > /dev/null \\\n", " "
);
${caseLoop} .= sprintf(
    "%${pfIndent}s && \${handlerFunc} \"%s\" \"%s\" \"%s\" \"%s\" \\\n"
  , " ", "\${sidecar}", "\${origParam}", "\${arg1}", "\${arg2}"
);
${caseLoop} .= sprintf(
    "%${pfIndent}s || checkAndAppend \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" \"%s\"\n"
  , " "
  , "\${arg1}"
  , "\${arg2}"
  , "\${arg3}"
  , "\${arg4}"
  , "\${arg5}"
  , "\${arg6}"
  , "\${arg7}"
  , "\${arg8}"
);
${caseLoop} .= sprintf("%${pfIndent}sret=\$?\n", " ");
${pfIndent} -= ${shiftWidth};

${caseLoop} .= sprintf("%${pfIndent}selse\n", " ");

${pfIndent} += ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}sret=0\n", " ");
${pfIndent} -= ${shiftWidth};

${caseLoop} .= sprintf("%${pfIndent}sfi\n", " ");

${pfIndent} -= ${shiftWidth};
${caseLoop} .= sprintf("%${pfIndent}sdone\n", " ");
${caseLoop} .= "\n";

# Complete generating the parser function.
${processFunc} .= ${caseLoop};

${processFunc} .= sprintf("%${pfIndent}sreturn \${ret}\n", " ");
${processFunc} .= "}\n";
${pfIndent} -= ${shiftWidth};

${processFunc} .= "\n";
${processFunc} .= "\n";
${processFunc} .= "longOptsList+=(${longOptsList})\n";
${processFunc} .= "\n";
${processFunc} .= "shortOptsList+=(${shortOptsList})\n";


# Complete generating the help function.
${helpFunc} .= sprintf("__EOF\n");
${helpFunc} .= "\n";
${helpFunc} .= sprintf("%${hfIndent}sreturn 0\n", " ");
${hfIndent} -= ${shiftWidth};

${helpFunc} .= "}\n";


# Output the two functions.
print ${helpFunc};
print "\n";
print "\n";
print(${processFunc});
