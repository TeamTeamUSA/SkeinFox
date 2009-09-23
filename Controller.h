//
//  Copyright 2009 Jordan Miller, Hive76. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface Controller : NSObject {
    NSMutableArray *gitBranches;
    NSUInteger currentBranch;
    IBOutlet NSPopUpButton *popUpButton;
    IBOutlet NSArrayController *myArrayController;
    NSNotificationCenter *notificationCenter;
}

@property (readwrite, retain) NSMutableArray *gitBranches;
@property (nonatomic, retain) IBOutlet NSPopUpButton *popUpButton;
@property (nonatomic, retain) IBOutlet NSArrayController *myArrayController;
@property (nonatomic, retain) NSNotificationCenter *notificationCenter;


// Send a notification to self that the user did update the git branch selection
- (void) didUpdateGitBranchSelection:(id)sender;

// Launch Skeinforge
- (void) launchSkeinforge:(id)sender;

@end
