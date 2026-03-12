# # """
# # Training Script for ArcFace Model on VGGFace2 Dataset
# # """

# # import torch
# # import torch.nn as nn
# # import torch.optim as optim
# # from torch.utils.data import Dataset, DataLoader
# # import torchvision.transforms as transforms
# # from pathlib import Path
# # import cv2
# # import numpy as np
# # from tqdm import tqdm
# # import os
# # import sys

# # # Add parent directory to path
# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # from backend.models.face_recognizer import ArcFaceModel


# # class VGGFace2Dataset(Dataset):
# #     """VGGFace2 Dataset Loader"""
    
# #     def __init__(self, root_dir, transform=None, max_classes=None):
# #         """
# #         Args:
# #             root_dir: Root directory of VGGFace2 dataset
# #             transform: Optional transform to be applied
# #             max_classes: Maximum number of identity classes to use
# #         """
# #         self.root_dir = Path(root_dir)
# #         self.transform = transform
        
# #         # Collect all images and labels
# #         self.samples = []
# #         self.class_to_idx = {}
        
# #         identity_dirs = sorted([d for d in self.root_dir.iterdir() if d.is_dir()])
        
# #         if max_classes:
# #             identity_dirs = identity_dirs[:max_classes]
        
# #         for idx, identity_dir in enumerate(identity_dirs):
# #             self.class_to_idx[identity_dir.name] = idx
            
# #             for img_path in identity_dir.glob('*.jpg'):
# #                 self.samples.append((str(img_path), idx))
        
# #         print(f"Loaded {len(self.samples)} images from {len(self.class_to_idx)} identities")
    
# #     def __len__(self):
# #         return len(self.samples)
    
# #     def __getitem__(self, idx):
# #         img_path, label = self.samples[idx]
        
# #         # Load image
# #         image = cv2.imread(img_path)
# #         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
# #         # Apply transforms
# #         if self.transform:
# #             image = self.transform(image)
        
# #         return image, label


# # def get_transforms(train=True):
# #     """Get data transforms"""
# #     if train:
# #         return transforms.Compose([
# #             transforms.ToPILImage(),
# #             transforms.Resize((128, 128)),
# #             transforms.RandomHorizontalFlip(),
# #             transforms.RandomRotation(15),
# #             transforms.ColorJitter(brightness=0.2, contrast=0.2),
# #             transforms.ToTensor(),
# #             transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
# #         ])
# #     else:
# #         return transforms.Compose([
# #             transforms.ToPILImage(),
# #             transforms.Resize((112, 112)),
# #             transforms.ToTensor(),
# #             transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
# #         ])


# # def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
# #     """Train for one epoch"""
# #     model.train()
# #     running_loss = 0.0
# #     correct = 0
# #     total = 0
    
# #     pbar = tqdm(dataloader, desc=f'Epoch {epoch}')
    
# #     for batch_idx, (images, labels) in enumerate(pbar):
# #         images = images.to(device)
# #         labels = labels.to(device)
        
# #         # Forward pass
# #         optimizer.zero_grad()
# #         outputs, embeddings = model(images, labels)
# #         loss = criterion(outputs, labels)
        
# #         # Backward pass
# #         loss.backward()
# #         optimizer.step()
        
# #         # Statistics
# #         running_loss += loss.item()
# #         _, predicted = outputs.max(1)
# #         total += labels.size(0)
# #         correct += predicted.eq(labels).sum().item()
        
# #         # Update progress bar
# #         pbar.set_postfix({
# #             'loss': running_loss / (batch_idx + 1),
# #             'acc': 100. * correct / total
# #         })
    
# #     epoch_loss = running_loss / len(dataloader)
# #     epoch_acc = 100. * correct / total
    
# #     return epoch_loss, epoch_acc


# # def validate(model, dataloader, criterion, device):
# #     """Validate the model"""
# #     model.eval()
# #     running_loss = 0.0
# #     correct = 0
# #     total = 0
    
# #     with torch.no_grad():
# #         for images, labels in tqdm(dataloader, desc='Validating'):
# #             images = images.to(device)
# #             labels = labels.to(device)
            
# #             outputs, embeddings = model(images, labels)
# #             loss = criterion(outputs, labels)
            
# #             running_loss += loss.item()
# #             _, predicted = outputs.max(1)
# #             total += labels.size(0)
# #             correct += predicted.eq(labels).sum().item()
    
# #     val_loss = running_loss / len(dataloader)
# #     val_acc = 100. * correct / total
    
# #     return val_loss, val_acc


# # def main():
# #     """Main training function"""
# #     # Configuration
# #     data_dir = 'data/vggface2/train'
# #     val_dir = 'data/vggface2/val'
# #     num_epochs = 50
# #     batch_size = 32
# #     learning_rate = 0.001
# #     embedding_size = 512
# #     num_classes = 9131  # VGGFace2 has 9,131 identities
# #     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
# #     print(f"Using device: {device}")
    
# #     # Create datasets
# #     train_transform = get_transforms(train=True)
# #     val_transform = get_transforms(train=False)
    
# #     train_dataset = VGGFace2Dataset(data_dir, transform=train_transform)
# #     val_dataset = VGGFace2Dataset(val_dir, transform=val_transform)
    
# #     # Create dataloaders
# #     train_loader = DataLoader(
# #         train_dataset,
# #         batch_size=batch_size,
# #         shuffle=True,
# #         num_workers=4,
# #         pin_memory=True
# #     )
    
# #     val_loader = DataLoader(
# #         val_dataset,
# #         batch_size=batch_size,
# #         shuffle=False,
# #         num_workers=4,
# #         pin_memory=True
# #     )
    
# #     # Initialize model
# #     model = ArcFaceModel(embedding_size=embedding_size, num_classes=num_classes)
# #     model = model.to(device)
    
# #     # Loss and optimizer
# #     criterion = nn.CrossEntropyLoss()
# #     optimizer = optim.Adam(model.parameters(), lr=learning_rate)
# #     scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    
# #     # Training loop
# #     best_val_acc = 0.0
    
# #     for epoch in range(1, num_epochs + 1):
# #         print(f"\n{'='*50}")
# #         print(f"Epoch {epoch}/{num_epochs}")
# #         print(f"{'='*50}")
        
# #         # Train
# #         train_loss, train_acc = train_epoch(
# #             model, train_loader, criterion, optimizer, device, epoch
# #         )
        
# #         # Validate
# #         val_loss, val_acc = validate(model, val_loader, criterion, device)
        
# #         # Learning rate scheduling
# #         scheduler.step()
        
# #         # Print results
# #         print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
# #         print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        
# #         # Save best model
# #         if val_acc > best_val_acc:
# #             best_val_acc = val_acc
# #             checkpoint = {
# #                 'epoch': epoch,
# #                 'state_dict': model.state_dict(),
# #                 'optimizer': optimizer.state_dict(),
# #                 'val_acc': val_acc,
# #             }
# #             torch.save(checkpoint, 'weights/arcface_r100_best.pth')
# #             print(f"✅ Saved best model with val_acc: {val_acc:.2f}%")
        
# #         # Save checkpoint every 5 epochs
# #         if epoch % 5 == 0:
# #             checkpoint = {
# #                 'epoch': epoch,
# #                 'state_dict': model.state_dict(),
# #                 'optimizer': optimizer.state_dict(),
# #                 'val_acc': val_acc,
# #             }
# #             torch.save(checkpoint, f'weights/arcface_r100_epoch{epoch}.pth')
    
# #     print(f"\n{'='*50}")
# #     print(f"Training completed!")
# #     print(f"Best validation accuracy: {best_val_acc:.2f}%")
# #     print(f"{'='*50}")


# # if __name__ == '__main__':
# #     main()

# """
# FAST ArcFace Training Script (VGGFace2)
# Speed Optimized Version
# """

# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import Dataset, DataLoader
# import torchvision.transforms as transforms
# from pathlib import Path
# import cv2
# import numpy as np
# from tqdm import tqdm
# import os
# import sys
# from torch.cuda.amp import autocast, GradScaler

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from backend.models.face_recognizer import ArcFaceModel


# # =========================================================
# # Early Stopping
# # =========================================================
# class EarlyStopping:
#     def __init__(self, patience=3, min_delta=0.1):
#         self.patience = patience
#         self.min_delta = min_delta
#         self.counter = 0
#         self.best_score = None

#     def __call__(self, val_acc):
#         if self.best_score is None:
#             self.best_score = val_acc
#             return False

#         if val_acc < self.best_score + self.min_delta:
#             self.counter += 1
#             print(f"⏳ EarlyStopping counter: {self.counter}/{self.patience}")
#             if self.counter >= self.patience:
#                 print("🛑 Early stopping triggered!")
#                 return True
#         else:
#             self.best_score = val_acc
#             self.counter = 0

#         return False


# # =========================================================
# # Dataset
# # =========================================================
# class VGGFace2Dataset(Dataset):

#     def __init__(self, root_dir, transform=None):
#         self.root_dir = Path(root_dir)
#         self.transform = transform
#         self.samples = []
#         self.class_to_idx = {}

#         identity_dirs = sorted([d for d in self.root_dir.iterdir() if d.is_dir()])

#         for idx, identity_dir in enumerate(identity_dirs):
#             self.class_to_idx[identity_dir.name] = idx
#             for img_path in identity_dir.glob('*.jpg'):
#                 self.samples.append((str(img_path), idx))

#         print(f"Loaded {len(self.samples)} images from {len(self.class_to_idx)} identities")

#     def __len__(self):
#         return len(self.samples)

#     def __getitem__(self, idx):
#         img_path, label = self.samples[idx]

#         # FAST WINDOWS IMAGE LOADING
#         image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#         if self.transform:
#             image = self.transform(image)

#         return image, label


# # =========================================================
# # Transforms (ArcFace uses 112x112)
# # =========================================================
# def get_transforms(train=True):
#     if train:
#         return transforms.Compose([
#             transforms.ToPILImage(),
#             transforms.Resize((112,112)),
#             transforms.RandomHorizontalFlip(),
#             transforms.ColorJitter(0.2,0.2),
#             transforms.ToTensor(),
#             transforms.Normalize([0.5]*3, [0.5]*3)
#         ])
#     else:
#         return transforms.Compose([
#             transforms.ToPILImage(),
#             transforms.Resize((112,112)),
#             transforms.ToTensor(),
#             transforms.Normalize([0.5]*3, [0.5]*3)
#         ])


# # =========================================================
# # Train
# # =========================================================
# def train_epoch(model, loader, criterion, optimizer, scaler, device, epoch):
#     model.train()
#     total_loss, correct, total = 0,0,0

#     pbar = tqdm(loader, desc=f"Epoch {epoch}")

#     for i,(images,labels) in enumerate(pbar):
#         images = images.to(device, non_blocking=True)
#         labels = labels.to(device, non_blocking=True)

#         optimizer.zero_grad()

#         with autocast(enabled=device.type=="cuda"):
#             outputs,_ = model(images,labels)
#             loss = criterion(outputs,labels)

#         scaler.scale(loss).backward()
#         scaler.step(optimizer)
#         scaler.update()

#         total_loss += loss.item()
#         _,pred = outputs.max(1)
#         total += labels.size(0)
#         correct += pred.eq(labels).sum().item()

#         pbar.set_postfix(loss=total_loss/(i+1), acc=100.*correct/total)

#     return total_loss/len(loader), 100.*correct/total


# # =========================================================
# # Validate
# # =========================================================
# def validate(model, loader, criterion, device):
#     model.eval()
#     total_loss, correct, total = 0,0,0

#     with torch.no_grad():
#         for images,labels in tqdm(loader,desc="Validating"):
#             images = images.to(device, non_blocking=True)
#             labels = labels.to(device, non_blocking=True)

#             with autocast(enabled=device.type=="cuda"):
#                 outputs,_ = model(images,labels)
#                 loss = criterion(outputs,labels)

#             total_loss += loss.item()
#             _,pred = outputs.max(1)
#             total += labels.size(0)
#             correct += pred.eq(labels).sum().item()

#     return total_loss/len(loader),100.*correct/total


# # =========================================================
# # Main
# # =========================================================
# def main():

#     # SPEED BOOST SETTINGS
#     torch.backends.cudnn.benchmark = True
#     torch.backends.cuda.matmul.allow_tf32 = True
#     torch.backends.cudnn.allow_tf32 = True

#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     print("Using device:",device)

#     data_dir="data/vggface2/train"
#     val_dir="data/vggface2/val"

#     batch_size = 32 if device.type=="cpu" else 128
#     num_epochs=10

#     train_dataset=VGGFace2Dataset(data_dir,get_transforms(True))
#     val_dataset=VGGFace2Dataset(val_dir,get_transforms(False))

#     num_classes=len(train_dataset.class_to_idx)
#     print("Detected identities:",num_classes)

#     train_loader=DataLoader(train_dataset,batch_size=batch_size,shuffle=True,
#                             num_workers=2,pin_memory=True,persistent_workers=True)

#     val_loader=DataLoader(val_dataset,batch_size=batch_size,shuffle=False,
#                           num_workers=2,pin_memory=True,persistent_workers=True)

#     model=ArcFaceModel(512,num_classes).to(device)

#     criterion=nn.CrossEntropyLoss()
#     optimizer=optim.Adam(model.parameters(),lr=0.001)
#     scheduler=optim.lr_scheduler.StepLR(optimizer,5,0.1)

#     scaler=GradScaler(enabled=device.type=="cuda")
#     early_stop=EarlyStopping(3,0.1)

#     os.makedirs("weights",exist_ok=True)
#     best_acc=0

#     for epoch in range(1,num_epochs+1):

#         print("\n"+"="*50)
#         print(f"Epoch {epoch}/{num_epochs}")
#         print("="*50)

#         train_loss,train_acc=train_epoch(model,train_loader,criterion,optimizer,scaler,device,epoch)
#         val_loss,val_acc=validate(model,val_loader,criterion,device)

#         scheduler.step()

#         print(f"\nTrain Loss:{train_loss:.4f} | Train Acc:{train_acc:.2f}%")
#         print(f"Val Loss:{val_loss:.4f} | Val Acc:{val_acc:.2f}%")

#         if val_acc>best_acc:
#             best_acc=val_acc
#             torch.save(model.state_dict(),"weights/arcface_fast_best.pth")
#             print("✅ Saved best model")

#         if early_stop(val_acc):
#             print(f"\nStopped early at epoch {epoch}")
#             break

#     print("\nTraining Complete | Best Acc:",best_acc)


# if __name__=="__main__":
#     main()


"""
FAST ArcFace Training Script (Correct ArcFace Usage)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from pathlib import Path
import cv2
import numpy as np
from tqdm import tqdm
import os
import sys
from torch.cuda.amp import autocast, GradScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models.face_recognizer import ArcFaceModel


# ================= Early Stopping =================
class EarlyStopping:
    def __init__(self, patience=3, min_delta=0.1):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None

    def __call__(self, val_acc):
        if self.best_score is None:
            self.best_score = val_acc
            return False

        if val_acc < self.best_score + self.min_delta:
            self.counter += 1
            print(f"⏳ EarlyStopping counter: {self.counter}/{self.patience}")
            if self.counter >= self.patience:
                print("🛑 Early stopping triggered!")
                return True
        else:
            self.best_score = val_acc
            self.counter = 0

        return False


# ================= Dataset =================
class VGGFace2Dataset(Dataset):

    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {}

        identity_dirs = sorted([d for d in self.root_dir.iterdir() if d.is_dir()])

        for idx, identity_dir in enumerate(identity_dirs):
            self.class_to_idx[identity_dir.name] = idx
            for img_path in identity_dir.glob('*.jpg'):
                self.samples.append((str(img_path), idx))

        print(f"Loaded {len(self.samples)} images from {len(self.class_to_idx)} identities")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if self.transform:
            image = self.transform(image)

        return image, label


# ================= Transforms =================
def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((112,112)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2,0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3,[0.5]*3)
        ])
    else:
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((112,112)),
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3,[0.5]*3)
        ])


# ================= Train =================
def train_epoch(model, loader, criterion, optimizer, scaler, device, epoch):
    model.train()
    total_loss, correct, total = 0,0,0

    pbar=tqdm(loader,desc=f"Epoch {epoch}")

    for i,(images,labels) in enumerate(pbar):
        images=images.to(device,non_blocking=True)
        labels=labels.to(device,non_blocking=True)

        optimizer.zero_grad()

        with autocast(enabled=device.type=="cuda"):
            outputs,_=model(images,labels)   # ArcFace margin applied ONLY here
            loss=criterion(outputs,labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss+=loss.item()
        _,pred=outputs.max(1)
        total+=labels.size(0)
        correct+=pred.eq(labels).sum().item()

        pbar.set_postfix(loss=total_loss/(i+1),acc=100.*correct/total)

    return total_loss/len(loader),100.*correct/total


# ================= Validate =================
def validate(model, loader, criterion, device):
    model.eval()
    total_loss,correct,total=0,0,0

    with torch.no_grad():
        for images,labels in tqdm(loader,desc="Validating"):
            images=images.to(device,non_blocking=True)
            labels=labels.to(device,non_blocking=True)

            with autocast(enabled=device.type=="cuda"):
                embeddings=model(images)  # NO LABELS → pure features
                W = torch.nn.functional.normalize(model.arcface.weight)
                cosine = torch.nn.functional.linear(embeddings, W)
                outputs = cosine * model.arcface.s

                loss = criterion(outputs, labels)

            total_loss+=loss.item()
            _,pred=outputs.max(1)
            total+=labels.size(0)
            correct+=pred.eq(labels).sum().item()

    return total_loss/len(loader),100.*correct/total


# ================= Main =================
def main():

    torch.backends.cudnn.benchmark=True
    torch.backends.cuda.matmul.allow_tf32=True
    torch.backends.cudnn.allow_tf32=True

    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:",device)

    batch_size=32 if device.type=="cpu" else 128
    num_epochs=10

    train_dataset=VGGFace2Dataset("data/vggface2/train",get_transforms(True))
    val_dataset=VGGFace2Dataset("data/vggface2/val",get_transforms(False))

    num_classes=len(train_dataset.class_to_idx)
    print("Detected identities:",num_classes)

    train_loader=DataLoader(train_dataset,batch_size=batch_size,shuffle=True,num_workers=2,pin_memory=True,persistent_workers=True)
    val_loader=DataLoader(val_dataset,batch_size=batch_size,shuffle=False,num_workers=2,pin_memory=True,persistent_workers=True)

    model=ArcFaceModel(512,num_classes).to(device)

    criterion=nn.CrossEntropyLoss()
    optimizer=optim.Adam(model.parameters(),lr=0.001)
    scheduler=optim.lr_scheduler.StepLR(optimizer,5,0.1)

    scaler=GradScaler(enabled=device.type=="cuda")
    early_stop=EarlyStopping(3,0.1)

    os.makedirs("weights",exist_ok=True)
    best_acc=0

    for epoch in range(1,num_epochs+1):

        print("\n"+"="*50)
        print(f"Epoch {epoch}/{num_epochs}")
        print("="*50)

        train_loss,train_acc=train_epoch(model,train_loader,criterion,optimizer,scaler,device,epoch)
        val_loss,val_acc=validate(model,val_loader,criterion,device)

        scheduler.step()

        print(f"\nTrain Loss:{train_loss:.4f} | Train Acc:{train_acc:.2f}%")
        print(f"Val Loss:{val_loss:.4f} | Val Acc:{val_acc:.2f}%")

        if val_acc>best_acc:
            best_acc=val_acc
            torch.save(model.state_dict(),"weights/arcface_fast_best.pth")
            print("✅ Saved best model")

        if early_stop(val_acc):
            print(f"\nStopped early at epoch {epoch}")
            break

    print("\nTraining Complete | Best Acc:",best_acc)


if __name__=="__main__":
    main()