//
//  Controller.h
//  NSPopUpButtonBindings
//
//  Created by Kevin Wojniak on 1/27/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import <Cocoa/Cocoa.h>


@interface Controller : NSObject {
	NSMutableArray *_things;
}

@property (readwrite, retain) NSMutableArray *things;

@end