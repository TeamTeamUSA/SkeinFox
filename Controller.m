//
//  Controller.m
//  NSPopUpButtonBindings
//
//  Created by Kevin Wojniak on 1/27/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

//Jordan Says:
/*
 This project and websites were from:
 http://forums.macrumors.com/showthread.php?t=420530
 http://www.cocoabuilder.com/archive/message/cocoa/2006/5/31/164724
 http://att.macrumors.com/attachment.php?attachmentid=99500&d=1201413221
 
 
 */

#import "Controller.h"
#import "gitBranch.h"


@implementation Controller

@synthesize things = _things;

- (void)awakeFromNib
{
	NSArray *names = [NSArray arrayWithObjects:@"Bird", @"Chair", @"Song", @"Computer", nil];
	NSMutableArray *things = [NSMutableArray array];
	for (NSString *name in names)
	{
		gitBranch *thing = [[[gitBranch alloc] init] autorelease];
		thing.name = name;
		[things addObject:thing];
	}
	
	self.things = things;
}

@end