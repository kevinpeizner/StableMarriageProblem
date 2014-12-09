import argparse
import pprint
import random
import pdb

description_string = """Stable Marriage Problem Simulator version 1, Copyright (C) 2014 Kevin Peizner
    Stable Marriage Problem Simulator comes with ABSOLUTELY NO WARRANTY; for details type `%(prog)s -w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `%(prog)s -c' for details."""

conditions_string = """a) You must cause the modified files to carry prominent notices
    stating that you changed the files and the date of any change.

    b) You must cause any work that you distribute or publish, that in
    whole or in part contains or is derived from the Program or any
    part thereof, to be licensed as a whole at no charge to all third
    parties under the terms of this License.

    c) If the modified program normally reads commands interactively
    when run, you must cause it, when started running for such
    interactive use in the most ordinary way, to print or display an
    announcement including an appropriate copyright notice and a
    notice that there is no warranty (or else, saying that you provide
    a warranty) and that users may redistribute the program under
    these conditions, and telling the user how to view a copy of this
    License.  (Exception: if the Program itself is interactive but
    does not normally print such an announcement, your work based on
    the Program is not required to print an announcement.)"""

warranty_string = """  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES."""

def select_best(b, cadidates, data):
    #pdb.set_trace()
    pList = data['priList']
    fiance = data['fiance']
    rank = data['f_rank']

    # Iterate through cadidates, finding the best one.
    tossed = []
    for c in cadidates:
        # First time member has received a proposal, just accept it.
        if(fiance == -1):
            fiance = c
            rank = pList.index(c)
            continue
        try:
            # Try to limit our search to only better cadidates: [0, rank).
            r = pList.index(c, 0, rank)
        except ValueError:
            # c is not a better cadidate, toss.
            tossed.append(c)
            continue
        else:
            # Trade up!
            if(r < rank):
                tossed.append(fiance)
                fiance = c
                rank = r
            else:
                # Should not be here, ValueError should have caught this case.
                assert 0
    
    return fiance, rank, tossed

def reject(group, proposals, data):
    rejects = []
    for b in group:
        if b in proposals:# and len(proposals[b]) > 1:
            # If b has been proposed to, pick the best...
            best, rank, rejected = select_best(b, proposals[b], data[b])

            # Update data structure.
            data[b]['fiance'] = best
            data[b]['f_rank'] = rank
            data[best]['fiance'] = b
            data[best]['f_rank'] = data[best]['priList'].index(b)
            
            rejects += rejected
            
    # All the rejected As, move on to the next cadidate...
    for a in rejects:
            data[a]['f_rank']+=1
            
    return data, rejects

def propose(group, data):
    new_proposals = {}
    for a in group:
        index = data[a]['f_rank']
        desired = data[a]['priList'][index]
        if desired in new_proposals:
            # desired has multiple proposals, add self to list of choices...
            new_proposals[desired].append(a)
        else:
            # desired is receiving first proposal...
            new_proposals[desired] = [a]
    return new_proposals

def simulate(groupA, groupB, dataDictionary):

    # Start off with all members of groupA treated as rejected,
    # and no proposals.
    # groupA is even #s
    # groupB is odd #s
    rejects = groupA
    proposals = {}
    
    #while rejects:
    proposals.update(propose(rejects, dataDictionary))
    pp.pprint(proposals)
    dataDictionary, rejects = reject(groupB, proposals, dataDictionary)
    #stable = check_stability(rejects, dataDictionary)
    pp.pprint(dataDictionary)
    pp.pprint(rejects)

    print('#################################')

    while rejects:
        proposals = propose(rejects, dataDictionary)
        pp.pprint(proposals)
        dataDictionary, rejects = reject(groupB, proposals, dataDictionary)
        #stable = check_stability(rejects, dataDictionary)
        pp.pprint(dataDictionary)
        pp.pprint(rejects)
    
    return

# Grenerate Priority Lists and other initial values
# and stuff them into a dictionary.
def generate_priorities(master, listA, listB):
    """Create priority lists for every member in master. Priority lists consist
    of only members of the opposite group. Prioritization is random. Add the list,
    initial list index, and initial fiance (-1 == no fiance) to a dictionary for
    each member.

    Returns a dictionary of this format:
    {MEMBER#: {'priList':LIST, 'fiance': -1, 'f_rank':0}}"""
    mDict = {}
    for member in master:
        if(member%2 == 0):
            # Memeber is from list A. Prioritize list B.
            shuffled = sorted(listB, key=lambda k: random.random())
        else:
            # Member is from list B. Prioritzie list A.
            shuffled = sorted(listA, key=lambda k: random.random())
        mDict[member] = {'priList':shuffled, 'fiance':-1, 'f_rank':0}

    # Sanity check
    if len(mDict) != len(master):
        return -1
    else:
        return mDict

# Odd numbers represent group A.
# Even numbers represent group B.
# Every pair will consist of one member
# from group A and one member from group B.
def setup_sim(n=0):
    """Based on input N, create a list of integers. If N is odd, use N+1.
    Group odd integers into group A, and even integers into group B.
    Generate priority lists for all members of both groups, such that the
    priority list for a given member is a ranked list of the memebers of the
    opposite group."""

    if n == 0:
        print('ERROR: Nothing to do. Sample size is', n)
        return # Error, nothing to do.
    if (n % 2) == 1:
        n+=1
        print('INFO: Sample size has been modified to', n)

    # Generate Lists.
    mList = range(n)
    aList = [x for x in mList if x%2 == 0]
    bList = [x for x in mList if x%2 == 1]

    pp.pprint(aList)
    pp.pprint(bList)

    # Grenerate Priority Lists and other initial values
    # and stuff them into a dictionary.
    mDict = generate_priorities(mList, aList, bList)

    #pp.pprint(mDict)
    return aList, bList, mDict


parser = argparse.ArgumentParser(description=description_string)
parser.add_argument('count', metavar='N', type=int, help='Number of people to simulate in a simulation.')
parser.add_argument('-s', '--step', action='store_true', help='Step through the simulation, pausing after each iteration.')
parser.add_argument('-w', '--warranty', action='store_true', help='Show software warranty details.')
parser.add_argument('-c', '--conditions', action='store_true', help='Show software distribution details.')
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)

#print(args)
groupA, groupB, dataDictionary = setup_sim(args.count)
simulate(groupA, groupB, dataDictionary)
