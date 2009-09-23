//
//  Copyright 2009 Jordan Miller, Hive76. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface Controller : NSObject {
    NSMutableArray *gitBranches;
    NSUInteger currentBranch;
    IBOutlet NSPopUpButton *popUpButton;
    IBOutlet NSWindow *window;
    IBOutlet NSArrayController *myArrayController;
    NSNotificationCenter *notificationCenter;
}

@property (readwrite, retain) NSMutableArray *gitBranches;
@property (nonatomic, retain) IBOutlet NSPopUpButton *popUpButton;
@property (nonatomic, retain) IBOutlet NSArrayController *myArrayController;
@property (nonatomic, retain) NSNotificationCenter *notificationCenter;


// Send a notification to self that the user did update the git branch selection
- (IBAction) didUpdateGitBranchSelection:(id)sender;

// Launch Skeinforge
- (IBAction) launchSkeinforge:(id)sender;

@end
