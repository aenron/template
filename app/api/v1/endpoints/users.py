"""
用户管理API端点
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.logging import logger
from app.core.exceptions import NotFoundException, ValidationException
from app.core.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash

# 创建路由器
router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[UserResponse]:
    """
    获取用户列表

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        db: 数据库会话

    Returns:
        用户列表
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        logger.info(f"获取用户列表成功，共{len(users)}条记录")
        return users
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """
    根据ID获取用户信息

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        用户信息

    Raises:
        NotFoundException: 用户不存在
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"用户ID {user_id} 不存在")

        logger.info(f"获取用户信息成功，用户ID: {user_id}")
        return user
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败，用户ID: {user_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_superuser)
) -> UserResponse:
    """
    创建新用户

    Args:
        user: 用户创建数据
        db: 数据库会话

    Returns:
        创建的用户信息

    Raises:
        ValidationException: 数据验证失败
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise ValidationException("用户名已存在")

        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise ValidationException("邮箱已存在")

        # 加密密码
        hashed_password = get_password_hash(user.password)

        # 创建新用户
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar=user.avatar,
            bio=user.bio,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"创建用户成功，用户ID: {db_user.id}")
        return db_user
    except ValidationException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建用户失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建用户失败")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    更新用户信息

    Args:
        user_id: 用户ID
        user_update: 用户更新数据
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        NotFoundException: 用户不存在
        ValidationException: 数据验证失败
    """
    try:
        # 查找用户
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise NotFoundException(f"用户ID {user_id} 不存在")

        # 检查用户名唯一性
        if user_update.username:
            existing_user = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
            if existing_user:
                raise ValidationException("用户名已存在")

        # 检查邮箱唯一性
        if user_update.email:
            existing_email = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
            if existing_email:
                raise ValidationException("邮箱已存在")

        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                # 加密新密码
                hashed_password = get_password_hash(value)
                setattr(db_user, "hashed_password", hashed_password)
            else:
                setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)

        logger.info(f"更新用户信息成功，用户ID: {user_id}")
        return db_user
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户信息失败，用户ID: {user_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="更新用户信息失败")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_superuser)
) -> dict:
    """
    删除用户

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        删除结果

    Raises:
        NotFoundException: 用户不存在
    """
    try:
        # 查找用户
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise NotFoundException(f"用户ID {user_id} 不存在")

        # 删除用户
        db.delete(db_user)
        db.commit()

        logger.info(f"删除用户成功，用户ID: {user_id}")
        return {"message": f"用户ID {user_id} 删除成功"}
    except NotFoundException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户失败，用户ID: {user_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="删除用户失败")


@router.get("/me/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """
    获取当前用户个人资料

    Args:
        current_user: 当前活跃用户

    Returns:
        用户个人资料
    """
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    更新当前用户个人资料

    Args:
        user_update: 用户更新数据
        db: 数据库会话
        current_user: 当前活跃用户

    Returns:
        更新后的用户信息

    Raises:
        ValidationException: 数据验证失败
    """
    try:
        # 检查用户名唯一性（排除当前用户）
        if user_update.username:
            existing_user = (
                db.query(User).filter(User.username == user_update.username, User.id != current_user.id).first()
            )
            if existing_user:
                raise ValidationException("用户名已存在")

        # 检查邮箱唯一性（排除当前用户）
        if user_update.email:
            existing_email = db.query(User).filter(User.email == user_update.email, User.id != current_user.id).first()
            if existing_email:
                raise ValidationException("邮箱已存在")

        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password":
                # 加密新密码
                hashed_password = get_password_hash(value)
                setattr(current_user, "hashed_password", hashed_password)
            else:
                setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        logger.info(f"用户个人资料更新成功，用户ID: {current_user.id}")
        return current_user
    except ValidationException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"用户个人资料更新失败，用户ID: {current_user.id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="个人资料更新失败")
